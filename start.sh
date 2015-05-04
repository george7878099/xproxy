#!/bin/bash

cd ./local
coproc PROXY { python2 proxy.py < /dev/null; }
cd ..
./checkip.sh
kill $PROXY_PID
