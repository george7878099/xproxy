@echo off

set GEVENT_LOOP=uvent.loop.UVLoop
set GEVENT_RESOLVER=gevent.resolver_thread.Resolver

cd /d %~dp0
cd local
.\goagent-uv.exe
cd ..
