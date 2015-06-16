#!/bin/bash

if [ "$*" == "-p" ]; then
	./checkip.sh </dev/null &
	CHECKIP_PID=`expr $!`
	./testip.sh </dev/null &
	TESTIP_PID=`expr $!`
	
	cd ./local
	python proxy.py </dev/null >/dev/null 2>&1
elif [ "$*" == "-c" ]; then
	./checkip.sh </dev/null >/dev/null 2>&1 &
	CHECKIP_PID=`expr $!`
	./testip.sh </dev/null >/dev/null 2>&1 &
	TESTIP_PID=`expr $!`
	
	cd ./local
	python proxy.py </dev/null
elif [ "$*" == "-a" ]; then
	./checkip.sh </dev/null >/dev/null 2>&1 &
	CHECKIP_PID=`expr $!`
	./testip.sh </dev/null >/dev/null 2>&1 &
	TESTIP_PID=`expr $!`
	
	cd ./local
	python proxy.py </dev/null >/dev/null 2>&1
else
	./checkip.sh </dev/null &
	CHECKIP_PID=`expr $!`
	./testip.sh </dev/null &
	TESTIP_PID=`expr $!`
	
	cd ./local
	python proxy.py </dev/null
fi

cd ..
pkill -P $CHECKIP_PID
pkill -P $TESTIP_PID
echo
