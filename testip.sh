#!/bin/bash

while true;
do
	rm ip_test.tmp;
	python ./checkip.py local/good_ip.txt;
	if [ $? -ne 0 ]; then
		exit;
	fi
	python ./addip.py ip_test.tmp local/good_ip.txt;
done;
