#!/bin/bash

while true;
do
	rm ip.tmp;
	rm ip_tmperror.tmp;
	rm ip_tmpno.tmp;
	rm ip_tmpok.tmp;
	./local/python27 ./checkip.py;
	if [ $? -ne 0 ]; then
		exit;
	fi
	./local/python27 ./addip.py ip.tmp local/good_ip.txt;
done;
