## Xproxy
* A proxy based on GoAgent and Checkgoogleip

## Linux
1. Requirements: python2.7.8 gevent-openssl(python) dnslib(python) pygeoip(python)
2. Install all required packages. Remember that python is python 2.7.8.
3. Download xproxy. Put your appid in local/proxy.ini.
4. ./start.sh.
5. Make sure the certificate(local/CA.crt) is installed.

## Windows
1. Install a MinGW environment. For example, [Git for Windows](https://git-scm.com/download/win) can provide this.
2. Download xproxy. Put your appid in local/proxy.ini.
3. ./start-win.sh.
5. Make sure the certificate(local/CA.crt) is installed.

## Links
* https://github.com/goagent/goagent
* https://github.com/moonshawdo/checkgoogleip
