#!/usr/bin/env python

import os
import platform
import subprocess
import sys
import time
import threading

if platform.system().lower()=="windows":
	python="python27"
else:
	python="python"

sys.path.append(os.path.dirname(__file__) or '.')

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
