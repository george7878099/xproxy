#!/bin/bash

KEEP_IP=100

while true;
do
	rm ip.tmp;
	rm ip_tmperror.tmp;
	rm ip_tmpno.tmp;
	rm ip_tmpok.tmp;
	python2 ./checkip.py;
	if [ $? -ne 0 ]; then
		exit;
	fi
	cat ip.tmp local/good_ip.txt > allip.tmp;
	head -$KEEP_IP allip.tmp > local/good_ip.txt;
	#one ip may appear more than once
	rm allip.tmp;
done;
