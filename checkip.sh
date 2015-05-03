#!/bin/bash

KEEP_IP=100

while true;
do
	rm ip.txt;
	rm ip_tmperror.txt;
	rm ip_tmpno.txt;
	rm ip_tmpok.txt;
	python2 ./checkip.py;
	if [ $? -ne 0 ]; then
		exit;
	fi
	cat ip.txt local/good_ip.txt > allip.txt;
	head -$KEEP_IP allip.txt > local/good_ip.txt;
	#one ip may appear more than once
	rm allip.txt;
done;
