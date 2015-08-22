@echo off

cd /d %~dp0
cd local
start .\python27 .\proxy.py
cd ..
