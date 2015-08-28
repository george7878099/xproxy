#!/usr/bin/env python

import ConfigParser
import os
import sys
import threading
import time
sys.path.append(os.path.dirname(__file__) or '.')

import addip
import checkip
import testip

checkip_threads=128
checkip_timeout=5
testip_enable=1
testip_timeout=5
testip_checkconn_addr="baidu.com"
testip_checkconn_timeout=2

def read_config():
	global checkip_threads,checkip_timeout,testip_enable,testip_timeout,testip_checkconn_addr,testip_checkconn_timeout
	conf=ConfigParser.ConfigParser()
	try:
		conf.read("iptool.ini")
		checkip_threads_tmp=conf.getint("checkip","threads")
		checkip_timeout_tmp=conf.getint("checkip","timeout")
		testip_enable_tmp=conf.getint("testip","enable")
		testip_timeout_tmp=conf.getint("testip","timeout")
		testip_checkconn_addr_tmp=conf.get("testip","checkconn_addr")
		testip_checkconn_timeout_tmp=conf.getint("testip","checkconn_timeout")
	except KeyboardInterrupt:
		addip.stop=True
		checkip_threads_tmp=0
		checkip_timeout_tmp=5
		testip_enable_tmp=0
		testip_timeout_tmp=5
		testip_checkconn_addr_tmp="baidu.com"
		testip_checkconn_timeout_tmp=2
	except:
		checkip_threads_tmp=128
		checkip_timeout_tmp=5
		testip_enable_tmp=1
		testip_timeout_tmp=5
		testip_checkconn_addr_tmp="baidu.com"
		testip_checkconn_timeout_tmp=2
	checkip_threads=checkip_threads_tmp
	checkip_timeout=checkip_timeout_tmp
	testip_enable=testip_enable_tmp
	testip_timeout=testip_timeout_tmp
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
