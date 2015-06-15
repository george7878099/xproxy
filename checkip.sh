#!/bin/bash

KEEP_IP=8192

while true;
do
	rm ip.tmp;
	rm ip_tmperror.tmp;
	rm ip_tmpno.tmp;
	rm ip_tmpok.tmp;
	python ./checkip.py;
	if [ $? -ne 0 ]; then
		exit;
	fi
	python ./addip.py ip.tmp local/good_ip.txt;
	rm ip_test.tmp;
	python ./checkip.py local/good_ip.txt;
	if [ $? -ne 0 ]; then
		exit;
	fi
	python ./addip.py ip_test.tmp local/good_ip.txt;
done;
