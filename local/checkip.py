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
g_checkipfile = os.path.join(g_filedir,"ip.txt")

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
				lst.append((begin,begin))
	return lst

def getiplist():
	lst=[]
	with open(g_checkipfile,"r") as f:
		for i in f:
			lst+=parseiprange(i)
	return lst

iplist=[]

threadcnt=0
threadcnt_lock=threading.Lock()

def checkipall():
	global iplist,threadcnt,threadcnt_lock
	try:
		iplist=getiplist()
		while True:
			time.sleep(2)
			while True:
				threadcnt_lock.acquire()
				if threadcnt<iptool.get_config("checkip","threads"):
					threadcnt+=1
					threadcnt_lock.release()
					t=threading.Thread(target=checkip)
					t.setDaemon(True)
					t.start()
				else:
					threadcnt_lock.release()
					break
	except KeyboardInterrupt:
		iptool.stop()

lock=threading.Lock()
checklst=set([])

def checkipsleep():
	i=0
	while i<iptool.get_config("checkip","interval"):
		time.sleep(1)
		i+=1

def checkipwork():
	global lock,checklst,iplist
	ipvalid=False
	try:
		time.sleep(0.25)
		ip=random.choice(iplist)
		ip=random.randint(ip[0],ip[1])
		ip=iptostr(ip)
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
			costtime=time.time()
			c = iptool.create_ssl_socket(ip, iptool.get_config("checkip","timeout"))
			costtime=int(time.time()*1000-costtime*1000)
			if iptool.test_connection(c)==iptool.TEST_OK:
				addip.addip(ip,costtime)
				logging.info("found ip %s, %d ms", ip, costtime)
			c.close()
		else:
			lock.release()
	except KeyboardInterrupt:
		iptool.stop()
	except:
		pass
	if ipvalid:
		try:
			checkipsleep()
		finally:
			with lock:
				checklst.remove(ip)

def checkip():
	global threadcnt,threadcnt_lock
	try:
		while True:
			with threadcnt_lock:
				if threadcnt>iptool.get_config("checkip","threads"):
					threadcnt-=1
					return
			checkipwork()
	except KeyboardInterrupt:
		iptool.stop()
	except:
		logging.exception("checkip exception")
		with threadcnt_lock:
			threadcnt-=1
