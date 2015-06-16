#!/bin/bash

while true;
do
	rm ip_test.tmp;
	./local/python27 ./checkip.py local/good_ip.txt;
	if [ $? -ne 0 ]; then
		exit;
	fi
	./local/python27 ./addip.py ip_test.tmp local/good_ip.txt;
done;
