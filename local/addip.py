#!/usr/bin/env python2

import os
import sys
import thread
import threading
import time
import traceback

sys.path.append(os.path.dirname(__file__) or '.')

import iptool

dst = "good_ip.txt"
tmpdst = "good_ip_tmp.tmp"
lock = threading.Lock()

sleeplock = threading.Lock()
sleep_before = 0

stop = False

def addtolist(item, iplist, ipset):
	global dst, lock
	try:
		if len(item) >= 2 and (item[0] not in ipset):
			iplist.append((int(item[1]), len(iplist), item[0]))
			ipset.add(item[0])
	except KeyboardInterrupt:
		iptool.stop()
	except:
		pass

def addip(ip, costtime):
	global dst, lock, stop
	if stop:
		iptool.stop()
	ipset = set([])
	iplist = []
	if ip:
		addtolist([ip, str(costtime)], iplist, ipset)
	try:
		with lock:
			with open(dst, "a"):
				pass
			with open(dst, "r") as ff:
				for strs in ff:
					addtolist(strs.strip("\n").strip("\r").split(" "), iplist, ipset)
			iplist.sort()
			iplist = iplist[:min(iptool.get_config("addip", "keep_ip"), len(iplist))]
			iptool.global_iplist = iplist
			if stop:
				iptool.stop()
			if ip:
				with open(tmpdst, "w") as ff:
					for i in iplist:
						ff.write(i[2] + " " + (str(i[0]) if i[0] >= 0 else "1000") + "\n")
				begin_time = time.time()
				while True:
					try:
						os.remove(dst)
					except OSError:
						cur_time = time.time()
						if cur_time >= begin_time and cur_time-begin_time <= 2:
							continue
					break
				os.rename(tmpdst, dst)
	except KeyboardInterrupt:
		iptool.stop()
	except:
		pass
