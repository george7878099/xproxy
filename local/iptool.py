#!/usr/bin/env python2

import ConfigParser
import copy
import os
import sys
import threading
import time
import traceback
sys.path.append(os.path.dirname(__file__) or '.')

import addip
import checkip
import testip

global_iplist = []
config_lock=threading.Lock()

iptool_config={("iptool","sleep_time"):0,
               ("addip","keep_ip"):8192,
               ("checkip","threads"):0,
               ("checkip","threads_low"):0,
               ("checkip","threads_low_count"):0,
               ("checkip","threads_low_time"):0,
               ("checkip","timeout"):1,
               ("checkip","interval"):0,
               ("testip","special"):0,
               ("testip","threads"):0,
               ("testip","timeout"):1,
               ("testip","interval"):1,
               ("testip","checkconn_addr"):"baidu.com",
               ("testip","checkconn_timeout"):2}

iptool_config_strings=set([("testip","checkconn_addr")])

def set_config(x):
	global iptool_config,config_lock
	config_lock.acquire()
	iptool_config=copy.deepcopy(x)
	config_lock.release()

def get_config(a=None,b=None):
	global iptool_config,config_lock
	ret=None
	if a==None and b==None:
		config_lock.acquire()
		ret=copy.deepcopy(iptool_config)
		config_lock.release()
	else:
		config_lock.acquire()
		ret=copy.deepcopy(iptool_config[(a,b)])
		config_lock.release()
	return ret

def read_config():
	global iptool_config_strings,global_iplist
	conf=ConfigParser.ConfigParser()
	try:
		conf.read("iptool.ini")
		iptool_config_tmp={}
		for i in get_config():
			if (i[0],i[1]) not in iptool_config_strings:
				iptool_config_tmp[i]=conf.getint(i[0],i[1])
			else:
				iptool_config_tmp[i]=conf.get(i[0],i[1])
		try:
			if global_iplist[iptool_config_tmp[("checkip","threads_low_count")]-1][0] <= iptool_config_tmp[("checkip","threads_low_time")]:
				iptool_config_tmp[("checkip","threads")]=iptool_config_tmp[("checkip","threads_low")]
		except KeyboardInterrupt:
			raise
		except:
			pass
		set_config(iptool_config_tmp)
	except KeyboardInterrupt:
		set_config({("iptool","sleep_time"):300,
		            ("addip","keep_ip"):8192,
		            ("checkip","threads"):0,
		            ("checkip","threads_low"):0,
		            ("checkip","threads_low_count"):0,
		            ("checkip","threads_low_time"):0,
		            ("checkip","timeout"):5,
		            ("checkip","interval"):0,
		            ("testip","special"):0,
		            ("testip","threads"):0,
		            ("testip","timeout"):5,
		            ("testip","interval"):5,
		            ("testip","checkconn_addr"):"baidu.com",
		            ("testip","checkconn_timeout"):2})
		stop()
	except:
		set_config({("iptool","sleep_time"):300,
		            ("addip","keep_ip"):8192,
		            ("checkip","threads"):128,
		            ("checkip","threads_low"):5,
		            ("checkip","threads_low_count"):100,
		            ("checkip","threads_low_time"):1000,
		            ("checkip","timeout"):5,
		            ("checkip","interval"):0,
		            ("testip","special"):7,
		            ("testip","threads"):10,
		            ("testip","timeout"):5,
		            ("testip","interval"):5,
		            ("testip","checkconn_addr"):"baidu.com",
		            ("testip","checkconn_timeout"):2})

def start():
	read_config()

	t1=threading.Thread(target=checkip.checkipall)
	t1.setDaemon(True)
	t1.start()
	t2=threading.Thread(target=testip.testipall)
	t2.setDaemon(True)
	t2.start()

	while True:
		try:
			time.sleep(2)
			read_config()
		except KeyboardInterrupt:
			stop()

def stop():
	addip.stop = True
	time.sleep(1)
	os._exit(0)

if __name__ == '__main__':
	try:
		start()
	except KeyboardInterrupt:
		stop()
	except:
		print traceback.format_exc()
