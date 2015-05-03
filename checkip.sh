#!/bin/bash

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
	cp ip.txt local/good_ip.txt;
done;
