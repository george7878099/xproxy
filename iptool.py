#!/usr/bin/env python

import os
import sys
import threading
import time
sys.path.append((os.path.dirname(__file__) or '.'))

import checkip
import testip

t=threading.Thread(target=checkip.checkipall)
t.setDaemon(True)
t.start()
t=threading.Thread(target=testip.testipall)
t.setDaemon(True)
t.start()

while(True):
	time.sleep(10000)
