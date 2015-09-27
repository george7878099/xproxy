#!/usr/bin/env python2

import ConfigParser
import os
import sys
import threading
import time
sys.path.append(os.path.dirname(__file__) or '.')

import addip
import checkip
import testip

iptool_sleep_time=300
addip_keep_ip=8192
checkip_threads=128
checkip_timeout=5
testip_special=1
testip_threads=10
testip_timeout=5
testip_interval=5
testip_checkconn_addr="baidu.com"
testip_checkconn_timeout=2

def read_config():
	global iptool_sleep_time,addip_keep_ip,checkip_threads,checkip_timeout,testip_special,testip_threads,testip_timeout,testip_interval,testip_checkconn_addr,testip_checkconn_timeout
	conf=ConfigParser.ConfigParser()
	try:
		conf.read("iptool.ini")
		iptool_sleep_time_tmp=conf.getint("iptool","sleep_time")
		addip_keep_ip_tmp=conf.getint("addip","keep_ip")
		checkip_threads_tmp=conf.getint("checkip","threads")
		checkip_timeout_tmp=conf.getint("checkip","timeout")
		testip_special_tmp=conf.getint("testip","special")
		testip_threads_tmp=conf.getint("testip","threads")
		testip_timeout_tmp=conf.getint("testip","timeout")
		testip_interval_tmp=conf.getint("testip","interval")
		testip_checkconn_addr_tmp=conf.get("testip","checkconn_addr")
		testip_checkconn_timeout_tmp=conf.getint("testip","checkconn_timeout")
	except KeyboardInterrupt:
		addip.stop=True
		iptool_sleep_time_tmp=300
		addip_keep_ip_tmp=8192
		checkip_threads_tmp=0
		checkip_timeout_tmp=5
		testip_special_tmp=0
		testip_threads_tmp=0
		testip_timeout_tmp=5
		testip_interval_tmp=5
		testip_checkconn_addr_tmp="baidu.com"
		testip_checkconn_timeout_tmp=2
	except:
		iptool_sleep_time_tmp=300
		addip_keep_ip_tmp=8192
		checkip_threads_tmp=128
		checkip_timeout_tmp=5
		testip_special_tmp=1
		testip_threads_tmp=10
		testip_timeout_tmp=5
		testip_interval_tmp=5
		testip_checkconn_addr_tmp="baidu.com"
		testip_checkconn_timeout_tmp=2
	iptool_sleep_time=iptool_sleep_time_tmp
	addip_keep_ip=addip_keep_ip_tmp
	checkip_threads=checkip_threads_tmp
	checkip_timeout=checkip_timeout_tmp
	testip_special=testip_special_tmp
	testip_threads=testip_threads_tmp
	testip_timeout=testip_timeout_tmp
	testip_interval=testip_interval_tmp
	testip_checkconn_addr=testip_checkconn_addr_tmp
	testip_checkconn_timeout=testip_checkconn_timeout_tmp

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
			addip.stop=True

if __name__ == '__main__':
	try:
		start()
	except KeyboardInterrupt:
		addip.stop=True
	except:
		print traceback.format_exc()
