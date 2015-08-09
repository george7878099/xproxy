#!/usr/bin/env python

import os
import platform
import subprocess
import sys
import sysconfig
import time
import threading

if platform.system().lower()=="windows":
	python="python27"
else:
	python="python"

try:
	import gevent.monkey
	gevent.monkey.patch_socket()
except:
	reload(sys).setdefaultencoding('UTF-8')
	sys.dont_write_bytecode = True
	sys.path = [(os.path.dirname(__file__) or '.') + '/packages.egg/noarch'] + sys.path + [(os.path.dirname(__file__) or '.') + '/packages.egg/' + sysconfig.get_platform().split('-')[0]]
	
	try:
	    __import__('gevent.monkey', fromlist=['.']).patch_all()
	except (ImportError, SystemError):
	    sys.exit(sys.stderr.write('please install python-gevent\n'))

import addip
import iptool

t=threading.Thread(target=iptool.start)
t.setDaemon(True)
t.start()

p=subprocess.Popen([python,"proxy.py"])

try:
	while(p.poll()==None and addip.stop==False):time.sleep(1)
except:
	pass

addip.stop=True
try:
	p.kill()
except:
	pass

time.sleep(1)
os._exit(0)
