#!/usr/bin/env python2

import os
import sys
import socket
import ssl
import httplib
import re
import select
import traceback
import logging
import random
import time
import threading

sys.path.append(os.path.dirname(__file__) or '.')
import addip
import iptool

g_filedir = os.path.dirname(__file__)
g_testipfile = os.path.join(g_filedir,"good_ip.txt")
g_cacertfile = os.path.join(g_filedir, "cacert.pem")

# Re-add sslwrap to Python 2.7.9
import inspect
__ssl__ = __import__('ssl')

try:
	_ssl = __ssl__._ssl
except AttributeError:
	_ssl = __ssl__._ssl2
	
def new_sslwrap(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=__ssl__.CERT_NONE, ssl_version=__ssl__.PROTOCOL_SSLv23, ca_certs=None, ciphers=None):
	context = __ssl__.SSLContext(ssl_version)
	context.verify_mode = cert_reqs or __ssl__.CERT_NONE
	if ca_certs:
		context.load_verify_locations(ca_certs)
	if certfile:
		context.load_cert_chain(certfile, keyfile)
	if ciphers:
		context.set_ciphers(ciphers)
		
	caller_self = inspect.currentframe().f_back.f_locals['self']
	return context._wrap_socket(sock, server_side=server_side, ssl_sock=caller_self)

if not hasattr(_ssl, 'sslwrap'):
	_ssl.sslwrap = new_sslwrap

def checkconnect(addr):
	try:
		if iptool.testip_checkconn_timeout<0:
			return True
		s=socket.socket(socket.AF_INET)
		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,True)
		s.settimeout(iptool.testip_checkconn_timeout)
		c = ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED,ca_certs=g_cacertfile)
		c.settimeout(iptool.testip_checkconn_timeout)
		c.connect((addr, 443))
		c.close()
	except KeyboardInterrupt:
		addip.stop=True
		return False
	except:
		return False
	return True

threadcnt=0
threadcnt_lock=threading.Lock()

def testipall():
	global threadcnt,threadcnt_lock
	try:
		for i in range(1,8):
			t=threading.Thread(target=testip,args=(i,))
			t.setDaemon(True)
			t.start()
		while True:
			while threadcnt<iptool.testip_threads:
				threadcnt_lock.acquire()
				threadcnt+=1
				threadcnt_lock.release()
				t=threading.Thread(target=testip,args=(0,))
				t.setDaemon(True)
				t.start()
			time.sleep(2)
	except KeyboardInterrupt:
		addip.stop=True

lock=threading.Lock()
checklst=set([])

def testipsleep():
	i=0
	while i<iptool.testip_interval:
		time.sleep(1)
		i+=1

def testipwork(mode):
	global lock,checklst
	ipvalid=False
	try:
		time.sleep(0.01)
		iperror=True
		ip=""
		with open(g_testipfile,"r") as f:
			if mode>0:
				for i in range(mode):
					tmpline=f.readline()
					if tmpline!="":ip=tmpline
					else:break
			else:
				lst=[]
				for i in f:
					lst.append(i)
				if len(lst)==0:ip=""
				else:ip=random.choice(lst)
		ip_split=ip.strip('\n').strip('\r').split(' ')
		try:
			if len(ip_split)>1 and int(ip_split[1])==2147483647:
				iperror=False
		except ValueError:
			pass
		ip=ip_split[0]
		if ip!="":
			lock.acquire()
			isin=ip in checklst
			if not isin:
				checklst.add(ip)
				lock.release()
				ipvalid=True
				testipsleep()
				while time.time()<addip.sleep_before:
					if(addip.sleep_before-time.time()>iptool.iptool_sleep_time):addip.sleep_before=0
					time.sleep(5)
				addip.sleep_before=0
				while (not checkconnect(iptool.testip_checkconn_addr)):
					time.sleep(1)
				costtime=time.time()
				s=socket.socket(socket.AF_INET)
				s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
				s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,True)
				s.settimeout(iptool.testip_timeout)
				c=ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED,ca_certs=g_cacertfile,ciphers='ECDHE-RSA-AES128-SHA')
				c.settimeout(iptool.testip_timeout)
				c.connect((ip, 443))
				costtime=int(time.time()*1000-costtime*1000)
				cert = c.getpeercert()
				if 'subject' in cert:
					for i in cert['subject']:
						if i[0][0]=='organizationName' and i[0][1]=='Google Inc':
							c.send("HEAD / HTTP/1.1\r\nAccept: */*\r\nHost: %s\r\n\r\n" % ip)
							response=httplib.HTTPResponse(c,buffering=True)
							response.begin()
							if "gws" in response.msg.dict["server"]:
								iperror=False
								addip.addip(ip,costtime)
							elif "google.com/sorry/" in response.msg.dict["location"]:
								iperror=False
								addip.sleeplock.acquire()
								if addip.sleep_before==0:
									addip.printlock.acquire()
									print ("iptool sleeps for %d secs" % iptool.iptool_sleep_time)
									addip.printlock.release()
								addip.sleep_before=time.time()+iptool.iptool_sleep_time
								addip.sleeplock.release()
							break
				c.close()
			else:
				lock.release()
				time.sleep(1)
	except KeyboardInterrupt:
		addip.stop=True
		return
	except:
		pass
	if ipvalid:
		if iperror:
			if checkconnect(iptool.testip_checkconn_addr):
				addip.addip(ip,2147483647)
		lock.acquire()
		checklst.remove(ip)
		lock.release()

def testip(mode):
	global threadcnt,threadcnt_lock
	try:
		while True:
			if mode>0:
				while iptool.testip_special==0:time.sleep(2)
			else:
				threadcnt_lock.acquire()
				if threadcnt>iptool.testip_threads:
					threadcnt-=1
					threadcnt_lock.release()
					return
				threadcnt_lock.release()
			testipwork(mode)
	except KeyboardInterrupt:
		addip.stop=True
