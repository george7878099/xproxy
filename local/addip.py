#!/usr/bin/env python2

import os
import sys
import thread
import threading
import time
import traceback

sys.path.append(os.path.dirname(__file__) or '.')

import iptool

dst="good_ip.txt"
tmpdst="good_ip_tmp.tmp"
lock=threading.Lock()

sleeplock=threading.Lock()
sleep_before=0
printlock=threading.Lock()

stop=False

def addtolist(item,iplist,ipset):
	global dst,lock,stop
	try:
		if len(item)>=2 and (item[0] not in ipset):
			iplist.append((int(item[1]),len(iplist),item[0]))
			ipset.add(item[0])
	except KeyboardInterrupt:
		stop=True
	except:
		pass

def addip(ip,costtime):
	global dst,lock,stop
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
		iplist=iplist[:min(iptool.get_config("addip","keep_ip"),len(iplist))]
		if stop:
			thread.exit()
		ff=open(tmpdst,"w")
		for i in iplist:
			ff.write(i[2]+" "+str(i[0])+"\n")
		ff.close()
		begin_time=time.time()
		while True:
			try:
				os.remove(dst)
			except OSError:
				cur_time=time.time()
				if cur_time>=begin_time and cur_time-begin_time<=2:
					continue
			break
		os.rename(tmpdst,dst)
	except KeyboardInterrupt:
		stop=True
		thread.exit()
	except:
		pass
	lock.release()
