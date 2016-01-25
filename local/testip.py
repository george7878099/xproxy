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

def checkconnect(addr):
	try:
		if iptool.get_config("testip","checkconn_timeout")<0:
			return True
		c = iptool.create_ssl_socket(addr, iptool.get_config("testip","checkconn_timeout"))
		c.close()
	except KeyboardInterrupt:
		iptool.stop()
	except:
		return False
	return True

special=set([])
special_lock=threading.Lock()
threadcnt=0
threadcnt_lock=threading.Lock()

def testipall():
	global special,special_lock,threadcnt,threadcnt_lock
	try:
		while True:
			for i in range(1,iptool.get_config("testip","special")+1):
				special_lock.acquire()
				if i not in special:
					special.add(i)
					special_lock.release()
					t=threading.Thread(target=testip,args=(i,))
					t.setDaemon(True)
					t.start()
				else:
					special_lock.release()
			while True:
				threadcnt_lock.acquire()
				if threadcnt<iptool.get_config("testip","threads"):
					threadcnt+=1
					threadcnt_lock.release()
					t=threading.Thread(target=testip,args=(0,))
					t.setDaemon(True)
					t.start()
				else:
					threadcnt_lock.release()
					break
			time.sleep(2)
	except KeyboardInterrupt:
		iptool.stop()

lock=threading.Lock()
checklst=set([])

def testipsleep():
	i=0
	while i<iptool.get_config("testip","interval"):
		time.sleep(1)
		i+=1

def testipwork(mode):
	global lock,checklst
	ipvalid=False
	try:
		time.sleep(0.01)
		iperror=True
		ip=""
		addip.addip("", 0)
		try:
			if mode>0:
				ip = iptool.global_iplist[mode - 1][2]
			else:
				ip = random.choice(iptool.global_iplist)[2]
		except KeyboardInterrupt:
			raise
		except:
			pass
		if ip:
			lock.acquire()
			isin=ip in checklst
			if not isin:
				checklst.add(ip)
				lock.release()
				ipvalid=True
				while time.time()<addip.sleep_before:
					if(addip.sleep_before-time.time()>iptool.get_config("iptool","sleep_time")):addip.sleep_before=0
					time.sleep(5)
				addip.sleep_before=0
				while (not checkconnect(iptool.get_config("testip","checkconn_addr"))):
					time.sleep(1)
				costtime=time.time()
				c = iptool.create_ssl_socket(ip, iptool.get_config("testip","timeout"))
				costtime=int(time.time()*1000-costtime*1000)
				cert = c.getpeercert()
				if 'subject' in cert:
					for i in cert['subject']:
						if i[0][0]=='organizationName' and i[0][1]=='Google Inc':
							c.send("HEAD /favicon.ico HTTP/1.1\r\nHost: goagent.appspot.com\r\n\r\n")
							response=httplib.HTTPResponse(c,buffering=True)
							response.begin()
							if "Google Frontend" in response.msg.dict["server"]:
								iperror=False
								addip.addip(ip,costtime)
							elif "google.com/sorry/" in response.msg.dict["location"]:
								iperror=False
								addip.sleeplock.acquire()
								if addip.sleep_before==0:
									logging.warn("iptool sleeps for %d secs", iptool.get_config("iptool","sleep_time"))
								addip.sleep_before=time.time()+iptool.get_config("iptool","sleep_time")
								addip.sleeplock.release()
							break
				c.close()
			else:
				lock.release()
				time.sleep(1)
	except KeyboardInterrupt:
		iptool.stop()
	except:
		pass
	if ipvalid:
		if iperror:
			if checkconnect(iptool.get_config("testip","checkconn_addr")):
				addip.addip(ip,2147483647)
		testipsleep()
		lock.acquire()
		checklst.remove(ip)
		lock.release()

def testip(mode):
	global special,special_lock,threadcnt,threadcnt_lock
	try:
		while True:
			if mode>0:
				if mode>iptool.get_config("testip","special"):
					special_lock.acquire()
					special.remove(mode)
					special_lock.release()
					return
			else:
				threadcnt_lock.acquire()
				if threadcnt>iptool.get_config("testip","threads"):
					threadcnt-=1
					threadcnt_lock.release()
					return
				threadcnt_lock.release()
			testipwork(mode)
	except KeyboardInterrupt:
		iptool.stop()
	except:
		logging.exception("testip exception")
		if mode>0:
			special_lock.acquire()
			special.remove(mode)
			special_lock.release()
		else:
			threadcnt_lock.acquire()
			threadcnt-=1
			threadcnt_lock.release()
