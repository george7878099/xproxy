## Xproxy
* A proxy based on GoAgent and Checkgoogleip

## Linux
* Requirements: python2.7.8 gevent-openssl(python) dnslib(python) pygeoip(python)
1. Install all the required packages. Remember that python is python 2.7.8.
2. Download xproxy. Put your appid in local/proxy.ini.
3. ./start.sh.
4. Install the certificate(local/CA.crt) if this hasn't been done.

## Windows
1. Install a MinGW environment. For example, Git for Windows can provide this.
2. Download xproxy. Put your appid in local/proxy.ini.
3. ./start-win.sh.
4. Install the certificate(local/CA.crt) if this hasn't been done.

## Links
* https://github.com/goagent/goagent
* https://github.com/moonshawdo/checkgoogleip
