#!/bin/bash

./checkip.sh <&- &
CHECKIP_PID=`expr $!`

cd ./local
python2 proxy.py <&-
cd ..

pkill -P $CHECKIP_PID
