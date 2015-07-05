#!/bin/bash

random=0
while true;
do
	rm ip_test.tmp;
	if [ $random -eq 0 ]; then
		python ./checkip.py local/good_ip.txt 7;
	else
		python ./checkip.py local/good_ip.txt -1;
	fi
	if [ $? -ne 0 ]; then
		exit;
	fi
	python ./addip.py ip_test.tmp local/good_ip.txt;
	random=`expr 1 - $random`
done;
