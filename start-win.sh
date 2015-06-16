#!/bin/bash

function setup_win(){
	export GEVENT_LOOP=uvent.loop.UVLoop
	export GEVENT_RESOLVER=block
	export GOAGENT_LISTEN_VISIBLE=1
}

if [ "$*" == "-p" ]; then
	./checkip-win.sh </dev/null &
	CHECKIP_PID=`expr $!`
	./testip-win.sh </dev/null &
	TESTIP_PID=`expr $!`
	
	cd ./local
	setup_win
	./python27 proxy.py </dev/null >/dev/null 2>&1
elif [ "$*" == "-c" ]; then
	./checkip-win.sh </dev/null >/dev/null 2>&1 &
	CHECKIP_PID=`expr $!`
	./testip-win.sh </dev/null >/dev/null 2>&1 &
	TESTIP_PID=`expr $!`
	
	cd ./local
	setup_win
	./python27 proxy.py </dev/null
elif [ "$*" == "-a" ]; then
	./checkip-win.sh </dev/null >/dev/null 2>&1 &
	CHECKIP_PID=`expr $!`
	./testip-win.sh </dev/null >/dev/null 2>&1 &
	TESTIP_PID=`expr $!`
	
	cd ./local
	setup_win
	./python27 proxy.py </dev/null >/dev/null 2>&1
else
	./checkip-win.sh </dev/null &
	CHECKIP_PID=`expr $!`
	./testip-win.sh </dev/null &
	TESTIP_PID=`expr $!`
	
	cd ./local
	setup_win
	./python27 proxy.py </dev/null
fi

cd ..
pkill -P $CHECKIP_PID
pkill -P $TESTIP_PID
echo
