#!/usr/bin/env python

import os
import sys
import threading
import time
sys.path.append(os.path.dirname(__file__) or '.')

import addip
import checkip
import testip

def start():
	t1=threading.Thread(target=checkip.checkipall)
	t1.setDaemon(True)
	t1.start()
	t2=threading.Thread(target=testip.testipall)
	t2.setDaemon(True)
	t2.start()

	while(True):
		time.sleep(10000)

if __name__ == '__main__':
	try:
		start()
	except KeyboardInterrupt:
		addip.stop=True
	except:
		print traceback.format_exc()
