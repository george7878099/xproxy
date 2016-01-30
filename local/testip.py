#!/usr/bin/env python2

import collections
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

def checkconnection(addr):
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

records = collections.deque()
records_lock = threading.Lock()

def testiprecord(time):
	with records_lock:
		records.appendleft(time)
		while len(records) > iptool.get_config("testip", "records"):
			records.pop()

def testipwork(mode):
	global lock,checklst
	ipvalid=False
	try:
		time.sleep(0.01)
		iperror=True
		ip=""
		addip.addip("", 0)
		try:
			if mode > 0:
				ip = [x[2] for x in iptool.global_iplist[:iptool.get_config("testip","special")]]
			else:
				ip = [x[2] for x in iptool.global_iplist]
			with lock:
				ip = [x for x in ip if x not in checklst]
				ip = random.choice(ip)
				checklst.add(ip)
		except KeyboardInterrupt:
			raise
		except:
			ip = ""
		if ip:
			ipvalid=True
			while time.time()<addip.sleep_before:
				if(addip.sleep_before-time.time()>iptool.get_config("iptool","sleep_time")):addip.sleep_before=0
				time.sleep(5)
			addip.sleep_before=0
			while (not checkconnection(iptool.get_config("testip","checkconn_addr"))):
				time.sleep(1)
			costtime=time.time()
			c = iptool.create_ssl_socket(ip, iptool.get_config("testip","timeout"))
			costtime=int(time.time()*1000-costtime*1000)
			result=iptool.test_connection(c)
			if result==iptool.TEST_OK:
				iperror=False
				addip.addip(ip,costtime)
				testiprecord(costtime)
			elif result==iptool.TEST_UNDEFINED:
				iperror=False
			c.close()
		else:
			time.sleep(1)
	except KeyboardInterrupt:
		iptool.stop()
	except:
		pass
	if ipvalid:
		try:
			if iperror:
				if checkconnection(iptool.get_config("testip","checkconn_addr")):
					addip.addip(ip, addip.TIME_INF)
					testiprecord(addip.TIME_INF)
			testipsleep()
		finally:
			with lock:
				checklst.remove(ip)

def testip(mode):
	global special,special_lock,threadcnt,threadcnt_lock
	try:
		while True:
			if mode>0:
				if mode>iptool.get_config("testip","special"):
					with special_lock:
						special.remove(mode)
					return
			else:
				with threadcnt_lock:
					if threadcnt>iptool.get_config("testip","threads"):
						threadcnt-=1
						return
			testipwork(mode)
	except KeyboardInterrupt:
		iptool.stop()
	except:
		logging.exception("testip exception")
		if mode>0:
			with special_lock:
				special.remove(mode)
		else:
			with threadcnt_lock:
				threadcnt-=1
