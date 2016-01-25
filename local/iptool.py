#!/usr/bin/env python2

import ConfigParser
import copy
import httplib
import os
import socket
import ssl
import sys
import threading
import time
import traceback

# Re-add sslwrap to Python 2.7.9
import inspect
__ssl__ = __import__('ssl')

try:
	_ssl = __ssl__._ssl
except AttributeError:
	_ssl = __ssl__._ssl2
	
def new_sslwrap(sock, server_side=False, keyfile=None, certfile=None, cert_reqs=__ssl__.CERT_NONE, ssl_version=__ssl__.PROTOCOL_SSLv23, ca_certs=None, ciphers=None):
	context = __ssl__.SSLContext(ssl_version)
	context.verify_mode = cert_reqs or __ssl__.CERT_NONE
	if ca_certs:
		context.load_verify_locations(ca_certs)
	if certfile:
		context.load_cert_chain(certfile, keyfile)
	if ciphers:
		context.set_ciphers(ciphers)
		
	caller_self = inspect.currentframe().f_back.f_locals['self']
	return context._wrap_socket(sock, server_side=server_side, ssl_sock=caller_self)

if not hasattr(_ssl, 'sslwrap'):
	_ssl.sslwrap = new_sslwrap

sys.path.append(os.path.dirname(__file__) or '.')

import addip
import checkip
import testip

global_iplist = []
config_lock=threading.Lock()

iptool_config={("iptool","sleep_time"):0,
               ("addip","keep_ip"):8192,
               ("checkip","threads"):0,
               ("checkip","threads_low"):0,
               ("checkip","threads_low_count"):0,
               ("checkip","threads_low_time"):0,
               ("checkip","timeout"):1,
               ("checkip","interval"):0,
               ("testip","special"):0,
               ("testip","threads"):0,
               ("testip","timeout"):1,
               ("testip","interval"):1,
               ("testip","checkconn_addr"):"baidu.com",
               ("testip","checkconn_timeout"):2}

iptool_config_strings=set([("testip","checkconn_addr")])

def set_config(x):
	global iptool_config,config_lock
	config_lock.acquire()
	iptool_config=copy.deepcopy(x)
	config_lock.release()

def get_config(a=None,b=None):
	global iptool_config,config_lock
	ret=None
	if a==None and b==None:
		config_lock.acquire()
		ret=copy.deepcopy(iptool_config)
		config_lock.release()
	else:
		with config_lock:
			ret=copy.deepcopy(iptool_config[(a,b)])
	return ret

def read_config():
	global iptool_config_strings,global_iplist
	conf=ConfigParser.ConfigParser()
	try:
		conf.read("iptool.ini")
		iptool_config_tmp={}
		for i in get_config():
			if (i[0],i[1]) not in iptool_config_strings:
				iptool_config_tmp[i]=conf.getint(i[0],i[1])
			else:
				iptool_config_tmp[i]=conf.get(i[0],i[1])
		try:
			addip.addip('', 0)
			if global_iplist[iptool_config_tmp[("checkip","threads_low_count")]-1][0] <= iptool_config_tmp[("checkip","threads_low_time")]:
				iptool_config_tmp[("checkip","threads")]=iptool_config_tmp[("checkip","threads_low")]
		except KeyboardInterrupt:
			raise
		except:
			pass
		set_config(iptool_config_tmp)
	except KeyboardInterrupt:
		set_config({("iptool","sleep_time"):300,
		            ("addip","keep_ip"):8192,
		            ("checkip","threads"):0,
		            ("checkip","threads_low"):0,
		            ("checkip","threads_low_count"):0,
		            ("checkip","threads_low_time"):0,
		            ("checkip","timeout"):5,
		            ("checkip","interval"):0,
		            ("testip","special"):0,
		            ("testip","threads"):0,
		            ("testip","timeout"):5,
		            ("testip","interval"):5,
		            ("testip","checkconn_addr"):"baidu.com",
		            ("testip","checkconn_timeout"):2})
		stop()
	except:
		set_config({("iptool","sleep_time"):300,
		            ("addip","keep_ip"):8192,
		            ("checkip","threads"):128,
		            ("checkip","threads_low"):5,
		            ("checkip","threads_low_count"):100,
		            ("checkip","threads_low_time"):1000,
		            ("checkip","timeout"):5,
		            ("checkip","interval"):0,
		            ("testip","special"):7,
		            ("testip","threads"):10,
		            ("testip","timeout"):5,
		            ("testip","interval"):5,
		            ("testip","checkconn_addr"):"baidu.com",
		            ("testip","checkconn_timeout"):2})

proxy_enable = False
proxy_host = ''
proxy_port = ''
proxy_username = ''
proxy_password = ''

g_filedir = os.path.dirname(__file__)
g_cacertfile = os.path.join(g_filedir, "cacert.pem")

def create_ssl_socket(ip, timeout):
	global proxy_enable, proxy_host, proxy_port, proxy_username, proxy_password
	c=None
	if not proxy_enable:
		s=socket.socket(socket.AF_INET)
		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,True)
		s.settimeout(timeout)
		c=ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED,ca_certs=g_cacertfile,ciphers='ECDHE-RSA-AES128-SHA')
		c.settimeout(timeout)
		c.connect((ip, 443))
	else:
		s=socket.socket(socket.AF_INET)
		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		s.setsockopt(socket.SOL_TCP,socket.TCP_NODELAY,True)
		s.settimeout(timeout)
		s.connect((proxy_host, int(proxy_port)))
		request_data = 'CONNECT %s:%s HTTP/1.1\r\n' % (ip, 443)
		if proxy_username and proxy_password:
			request_data += 'Proxy-Authorization: Basic %s\r\n' % base64.b64encode(('%s:%s' % (proxy_username, proxy_password)).encode()).decode().strip()
		request_data += '\r\n'
		s.sendall(request_data)
		response = httplib.HTTPResponse(s)
		response.fp.close()
		response.fp = s.makefile('rb', 0)
		response.begin()
		if response.status >= 400:
			raise socket.error('%s %s %s' % (response.version, response.status, response.reason))
		c=ssl.wrap_socket(s,cert_reqs=ssl.CERT_REQUIRED,ca_certs=g_cacertfile,ciphers='ECDHE-RSA-AES128-SHA', do_handshake_on_connect=False)
		c.settimeout(timeout)
		c.do_handshake()
	return c

def start():
	read_config()

	t1=threading.Thread(target=checkip.checkipall)
	t1.setDaemon(True)
	t1.start()
	t2=threading.Thread(target=testip.testipall)
	t2.setDaemon(True)
	t2.start()

	while True:
		try:
			time.sleep(2)
			read_config()
		except KeyboardInterrupt:
			stop()

def stop():
	addip.stop = True
	time.sleep(1)
	os._exit(0)

if __name__ == '__main__':
	try:
		start()
	except KeyboardInterrupt:
		stop()
	except:
		print traceback.format_exc()
