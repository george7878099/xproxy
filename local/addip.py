#!/usr/bin/env python

import os
import sys
import thread
import threading
import traceback

keep_ip=8192
dst="good_ip.txt"
lock=threading.Lock()

sleeplock=threading.Lock()
sleep_before=0
printlock=threading.Lock()

stop=False

def addtolist(item,iplist,ipset):
	global keep_ip,dst,lock,stop
	try:
		if len(item)>=2 and (item[0] not in ipset):
			iplist.append((int(item[1]),item[0]))
			ipset.add(item[0])
	except KeyboardInterrupt:
		stop=True
	except:
		pass

def addip(ip,costtime):
	global keep_ip,dst,lock,stop
	if stop:
		thread.exit()
	ipset=set([])
	iplist=[]
	addtolist([ip,str(costtime)],iplist,ipset)
	lock.acquire()
	try:
		ff=open(dst,"a")
		ff.close()
		ff=open(dst,"r")
		for strs in ff:
			addtolist(strs.strip("\n").strip("\r").split(" "),iplist,ipset)
		ff.close()
		iplist.sort()
		iplist=iplist[:min(keep_ip,len(iplist))]
		if stop:
			thread.exit()
		try:ff=open(dst,"w")
		except:pass
		try:
			for i in iplist:
				try:ff.write(i[1]+" "+str(i[0])+"\n")
				except:pass
		except:pass
		ff.close()
	except KeyboardInterrupt:
		stop=True
		thread.exit()
	except:
		pass
	lock.release()
