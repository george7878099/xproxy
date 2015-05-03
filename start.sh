#!/bin/bash

cd ./local && python2 proxy.py &
proxy_PID=$!
./checkip.sh
kill $proxy_PID
