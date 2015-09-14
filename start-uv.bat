@echo off

set GEVENT_LOOP=uvent.loop.UVLoop
set GEVENT_RESOLVER=block

cd /d %~dp0
cd local
start .\python27 .\start.py
cd ..
