#!/bin/bash

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
done;
