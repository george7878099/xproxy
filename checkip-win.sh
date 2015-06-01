#!/bin/bash

KEEP_IP=8192

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
	cat ip.tmp local/good_ip.txt | awk '!a[$0]++' | head -$KEEP_IP > good.tmp;
	mv good.tmp local/good_ip.txt;
done;
