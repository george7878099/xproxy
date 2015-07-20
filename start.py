#!/usr/bin/env python

import os
import platform
import subprocess
import time

pf=platform.system().lower()
if pf=="windows":
	prefix="local\\python27"
	slash="\\"
else:
	prefix="python"
	slash="/"
p=[None,None]

p[0]=subprocess.Popen([prefix,"proxy.py"],cwd="local")
p[1]=subprocess.Popen([prefix,"iptool.py"])

try:
	while(p[0].poll()==None and p[1].poll()==None):
		time.sleep(1)
except KeyboardInterrupt:
	pass

for x in p:
	try:
		x.terminate()
	except:
		pass

time.sleep(0.5)

try:
	os.remove("good_ip.tmp")
except:
	pass
