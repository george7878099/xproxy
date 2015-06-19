#!/usr/bin/env python

import sys

keep_ip=8192
ipset=set([])
iplist=[]

def add(item):
    if len(item)>=2 and (item[0] not in ipset):
        ipset.add(item[0])
        iplist.append((int(item[1]),item[0]))

def sort():
    iplist.sort()

def addip(src,dst):
    global iplist
    ff=open(src,"r+")
    for strs in ff:
        add(strs.strip("\n").strip("\r").split(" "))
    ff=open(dst,"a+")
    ff.close()
    ff=open(dst,"r+")
    for strs in ff:
        add(strs.strip("\n").strip("\r").split(" "))
    sort()
    ff=open(dst,"w")
    iplist=iplist[:min(keep_ip,len(iplist))]
    for i in iplist:
        ff.write(i[1]+" "+str(i[0])+"\n")

if len(sys.argv)>2:
    addip(sys.argv[1],sys.argv[2])
