#!/usr/bin/env python

import os
import sys
import threading

keep_ip=8192
dst="local/good_ip.txt"
tmp="good_ip.tmp"
lock=threading.Lock()

sleeplock=threading.Lock()
sleep_before=0
printlock=threading.Lock()

def addtolist(item,iplist,ipset):
	global keep_ip,dst,tmp,lock
	try:
		if len(item)>=2 and (item[0] not in ipset):
			iplist.append((int(item[1]),item[0]))
			ipset.add(item[0])
	except:
		pass

def addip(ip,costtime):
	global keep_ip,dst,tmp,lock
	ipset=set([])
	iplist=[]
	addtolist([ip,str(costtime)],iplist,ipset)
	ff=open(dst,"a+")
	ff.close()
	ff=open(dst,"r")
	for strs in ff:
		addtolist(strs.strip("\n").strip("\r").split(" "),iplist,ipset)
	ff.close()
	iplist.sort()
	lock.acquire()
	try:
		ff=open(tmp,"w")
		iplist=iplist[:min(keep_ip,len(iplist))]
		for i in iplist:
			ff.write(i[1]+" "+str(i[0])+"\n")
		ff.close()
		os.rename(tmp,dst)
	except:
		pass
	lock.release()
