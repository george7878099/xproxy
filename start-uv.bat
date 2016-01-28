@echo off

cd /d %~dp0
cd local
start .\xproxy-uv.exe
cd ..
