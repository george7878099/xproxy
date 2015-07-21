#!/usr/bin/env python

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

g_filedir = os.path.dirname(__file__)
g_checkipfile = os.path.join(g_filedir,"ip.txt")
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

def iptoint(ip):
	try:
		s=ip.split('.')
		s=[int(x) for x in s]
		return (s[0]<<8*3)+(s[1]<<8*2)+(s[2]<<8)+s[3]
	except:
		return 0

def iptostr(ip):
	return str(ip>>8*3)+'.'+str((ip>>8*2)&255)+'.'+str((ip>>8)&255)+'.'+str(ip&255)

def parseiprange(ip):
	if ip.startswith('#'):
		return []
	ip=ip.strip(' ').strip('\n').strip('\r')
	l=ip.split('|')
	lst=[]
	for i in l:
		if '/' in i:
			(main,mask)=i.split('/')
			main=iptoint(main)
			mask=int(mask)
			if main==0 or mask<0 or mask>32:continue
			revmask=(1<<(32-mask))-1
			mask=0xffffffff^revmask
			lst.append((main&mask,((main&mask)|revmask)))
		elif '-' in i:
			(begin,end)=i.split('-')
			if len(end)<=3:
				end=begin[0:begin.rfind(".")]+"."+end
			begin=iptoint(begin)
			end=iptoint(end)
			if begin==0 or end==0:continue
			lst.append((begin,end))
		elif i.endswith('.'):
			begin=iptoint(i+"0")
			end=iptoint(i+"255")
			if begin==0 or end==0:continue
			lst.append((begin,end))
		else:
			begin=iptoint(i)
			if begin!=0:
				lst.append(begin,begin)
	return lst

def getiplist():
	lst=[]
	with open(g_checkipfile,"r") as f:
		for i in f:
			lst+=parseiprange(i)
	return lst

maxthreadcnt=128
iplist=[]

def checkipall():
	global iplist,maxthreadcnt
	try:
		iplist=getiplist()
		for i in range(maxthreadcnt):
			t=threading.Thread(target=checkip)
			t.setDaemon(True)
			t.start()
		while(True):
			time.sleep(10000)
	except KeyboardInterrupt:
		addip.stop=True

lock=threading.Lock()
checklst=set([])

def checkip():
	global lock,checklst,iplist
	while(True):
		try:
			ipvalid=False
			ip=random.choice(iplist)
			ip=random.randint(ip[0],ip[1])
			ip=iptostr(ip)
			lock.acquire()
			isin=ip in checklst
			if not isin:
				checklst.add(ip)
				lock.release()
				ipvalid=True
				while(time.time()<addip.sleep_before):
					if(addip.sleep_before-time.time()>300):addip.sleep_before=0
					time.sleep(5)
				addip.sleep_before=0
				costtime=time.time()
				s=socket.socket(socket.AF_INET)
				s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
				s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,True)
				s.settimeout(5)
				c=ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED,ca_certs=g_cacertfile,ciphers='ECDHE-RSA-AES128-SHA')
				c.settimeout(5)
				c.connect((ip, 443))
				costtime=int(time.time()*1000-costtime*1000)
				cert = c.getpeercert()
				if 'subject' in cert:
					for i in cert['subject']:
						if i[0][0]=='organizationName' and i[0][1]=='Google Inc':
							c.send("HEAD / HTTP/1.1\r\nAccept: */*\r\nHost: %s\r\n\r\n" % ip)
							response=httplib.HTTPResponse(c,buffering=True)
							response.begin()
							server=response.msg.dict["server"]
							if "gws" in server:
								addip.addip(ip,costtime)
								addip.printlock.acquire()
								print("found ip %s, %d ms" % (ip,costtime))
								addip.printlock.release()
							elif "google.com/sorry/" in response.msg.dict["location"]:
								addip.sleeplock.acquire()
								if addip.sleep_before==0:
									addip.printlock.acquire()
									print "iptool sleeps for 300 secs"
									addip.printlock.release()
								addip.sleep_before=time.time()+300
								addip.sleeplock.release()
							break
				c.close()
			else:
				lock.release()
		except KeyboardInterrupt:
			addip.stop=True
			return
		except:
			pass
		if ipvalid:
			lock.acquire()
			checklst.remove(ip)
			lock.release()

if __name__ == '__main__':
	try:
		checkipall()
	except KeyboardInterrupt:
		addip.stop=True
	except:
		print traceback.format_exc()