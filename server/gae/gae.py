#!/usr/bin/env python
# coding:utf-8

__version__ = '4.0.0'
__password__ = ''
__hostsdeny__ = ()  # __hostsdeny__ = ('.youtube.com', '.youku.com')

import os
import re
import time
import struct
import zlib
import base64
import logging
import urlparse
import httplib
import io
import string

from google.appengine.api import urlfetch
from google.appengine.api.taskqueue.taskqueue import MAX_URL_LENGTH
from google.appengine.runtime import apiproxy_errors

URLFETCH_MAX = 2
URLFETCH_MAXSIZE = 4*1024*1024
URLFETCH_DEFLATE_MAXSIZE = 4*1024*1024
URLFETCH_TIMEOUT = 30

def message_html(title, banner, detail=''):
    MESSAGE_TEMPLATE = '''
    <html><head>
    <meta http-equiv="content-type" content="text/html;charset=utf-8">
    <title>$title</title>
    <style><!--
    body {font-family: arial,sans-serif}
    div.nav {margin-top: 1ex}
    div.nav A {font-size: 10pt; font-family: arial,sans-serif}
    span.nav {font-size: 10pt; font-family: arial,sans-serif; font-weight: bold}
    div.nav A,span.big {font-size: 12pt; color: #0000cc}
    div.nav A {font-size: 10pt; color: black}
    A.l:link {color: #6f6f6f}
    A.u:link {color: green}
    //--></style>
    </head>
    <body text=#000000 bgcolor=#ffffff>
    <table border=0 cellpadding=2 cellspacing=0 width=100%>
    <tr><td bgcolor=#3366cc><font face=arial,sans-serif color=#ffffff><b>Message From FetchServer</b></td></tr>
    <tr><td> </td></tr></table>
    <blockquote>
    <H1>$banner</H1>
    $detail
    <p>
    </blockquote>
    <table width=100% cellpadding=0 cellspacing=0><tr><td bgcolor=#3366cc><img alt="" width=1 height=4></td></tr></table>
    </body></html>
    '''
    return string.Template(MESSAGE_TEMPLATE).substitute(title=title, banner=banner, detail=detail)


try:
    from Crypto.Cipher.ARC4 import new as RC4Cipher
except ImportError:
    logging.warn('Load Crypto.Cipher.ARC4 Failed, Use Pure Python Instead.')
    class RC4Cipher(object):
        def __init__(self, key):
            x = 0
            box = range(256)
            for i, y in enumerate(box):
                x = (x + y + ord(key[i % len(key)])) & 0xff
                box[i], box[x] = box[x], y
            self.__box = box
            self.__x = 0
            self.__y = 0
        def encrypt(self, data):
            out = []
            out_append = out.append
            x = self.__x
            y = self.__y
            box = self.__box
            for char in data:
                x = (x + 1) & 0xff
                y = (y + box[x]) & 0xff
                box[x], box[y] = box[y], box[x]
                out_append(chr(ord(char) ^ box[(box[x] + box[y]) & 0xff]))
            self.__x = x
            self.__y = y
            return ''.join(out)


def inflate(data):
    return zlib.decompress(data, -zlib.MAX_WBITS)


def deflate(data):
    return zlib.compress(data)[2:-4]


def format_response(status, headers, content):
    if content:
        headers.pop('content-length', None)
        headers['Content-Length'] = str(len(content))
    data = 'HTTP/1.1 %d %s\r\n%s\r\n\r\n%s' % (status, httplib.responses.get(status, 'Unknown'), '\r\n'.join('%s: %s' % (k.title(), v) for k, v in headers.items()), content)
    data = deflate(data)
    return struct.pack('!h', len(data)) + data


def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET' and 'HTTP_X_URLFETCH_PS1' not in environ:
        timestamp = long(os.environ['CURRENT_VERSION_ID'].split('.')[1])/2**28
        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp+8*3600))
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield 'GoAgent Python Server %s works, deployed at %s\n' % (__version__, ctime)
        if len(__password__) > 2:
            yield 'Password: %s%s%s' % (__password__[0], '*'*(len(__password__)-2), __password__[-1])
        raise StopIteration

    if environ['REQUEST_METHOD'] == 'HEAD':
        start_response('200 OK', [('Content-Type', 'image/gif')])
        raise StopIteration

    options = environ.get('HTTP_X_URLFETCH_OPTIONS', '')
    if 'rc4' in options and not __password__:
        start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('400 Bad Request', 'Bad Request (options) - please set __password__ in gae.py', 'please set __password__ and upload gae.py again')
        raise StopIteration

    try:
        if 'HTTP_X_URLFETCH_PS1' in environ:
            payload = inflate(base64.b64decode(environ['HTTP_X_URLFETCH_PS1']))
            body = inflate(base64.b64decode(environ['HTTP_X_URLFETCH_PS2'])) if 'HTTP_X_URLFETCH_PS2' in environ else ''
        else:
            wsgi_input = environ['wsgi.input']
            input_data = wsgi_input.read(int(environ.get('CONTENT_LENGTH', '0')))
            if 'rc4' in options:
                input_data = RC4Cipher(__password__).encrypt(input_data)
            payload_length, = struct.unpack('!h', input_data[:2])
            payload = inflate(input_data[2:2+payload_length])
            body = input_data[2+payload_length:]
        raw_response_line, payload = payload.split('\r\n', 1)
        method, url = raw_response_line.split()[:2]
        headers = {}
        for line in payload.splitlines():
            key, value = line.split(':', 1)
            headers[key.title()] = value.strip()
    except (zlib.error, KeyError, ValueError):
        import traceback
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('500 Internal Server Error', 'Bad Request (payload) - Possible Wrong Password', '<pre>%s</pre>' % traceback.format_exc())
        raise StopIteration

    kwargs = {}
    any(kwargs.__setitem__(x[len('x-urlfetch-'):].lower(), headers.pop(x)) for x in headers.keys() if x.lower().startswith('x-urlfetch-'))

    logging.info('%s "%s %s %s" - -', environ['REMOTE_ADDR'], method, url, 'HTTP/1.1')

    if __password__ and __password__ != kwargs.get('password', ''):
        start_response('403 Forbidden', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('403 Wrong password', 'Wrong password(%r)' % kwargs.get('password', ''), 'GoAgent proxy.ini password is wrong!')
        raise StopIteration

    netloc = urlparse.urlparse(url).netloc

    if __hostsdeny__ and netloc.endswith(__hostsdeny__):
        start_response('403 Forbidden', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('403 Hosts Deny', 'Hosts Deny(%r)' % netloc, detail='url=%r' % url)
        raise StopIteration

    if len(url) > MAX_URL_LENGTH:
        start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('400 Bad Request', 'length of URL too long(greater than %r)' % MAX_URL_LENGTH, detail='url=%r' % url)
        raise StopIteration

    if netloc.startswith(('127.0.0.', '::1', 'localhost')):
        start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('GoAgent %s is Running' % __version__, 'Now you can visit some websites', ''.join('<a href="https://%s/">%s</a><br/>' % (x, x) for x in ('google.com', 'mail.google.com')))
        raise StopIteration

    fetchmethod = getattr(urlfetch, method, None)
    if not fetchmethod:
        start_response('405 Method Not Allowed', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('405 Method Not Allowed', 'Method Not Allowed: %r' % method, detail='Method Not Allowed URL=%r' % url)
        raise StopIteration

    if 'Content-Encoding' in headers and body:
        if headers['Content-Encoding'] == 'deflate':
            body = inflate(body)
            headers['Content-Length'] = str(len(body))
            del headers['Content-Encoding']

    timeout = int(kwargs.get('timeout', URLFETCH_TIMEOUT))
    validate_certificate = bool(int(kwargs.get('validate', 0)))
    maxsize = int(kwargs.get('maxsize', 0))
    # https://www.freebsdchina.org/forum/viewtopic.php?t=54269
    accept_encoding = headers.get('Accept-Encoding', '') or headers.get('Bccept-Encoding', '')
    errors = []
    for i in xrange(int(kwargs.get('fetchmax', URLFETCH_MAX))):
        try:
            response = urlfetch.fetch(url, body, fetchmethod, headers, allow_truncated=False, follow_redirects=False, deadline=timeout, validate_certificate=validate_certificate)
            break
        except apiproxy_errors.OverQuotaError as e:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
            yield message_html('500 Urlfetch Error', 'Urlfetch Over Quota')
            raise StopIteration
        except urlfetch.DeadlineExceededError as e:
            errors.append('%r, timeout=%s' % (e, timeout))
            logging.error('DeadlineExceededError(timeout=%s, url=%r)', timeout, url)
            timeout *= 2
        except urlfetch.DownloadError as e:
            errors.append('%r, timeout=%s' % (e, timeout))
            logging.error('DownloadError(timeout=%s, url=%r)', timeout, url)
            timeout *= 2
        except urlfetch.ResponseTooLargeError as e:
            errors.append('%r, timeout=%s' % (e, timeout))
            response = e.response
            logging.error('ResponseTooLargeError(timeout=%s, url=%r) response(%r)', timeout, url, response)
            m = re.search(r'=\s*(\d+)-', headers.get('Range') or headers.get('range') or '')
            if m is None:
                headers['Range'] = 'bytes=0-%d' % (maxsize or URLFETCH_MAXSIZE)
            else:
                headers.pop('Range', '')
                headers.pop('range', '')
                start = int(m.group(1))
                headers['Range'] = 'bytes=%s-%d' % (start, start+(maxsize or URLFETCH_MAXSIZE))
            timeout *= 2
        except urlfetch.SSLCertificateError as e:
            errors.append('%r, should validate=0 ?' % e)
            logging.error('%r, timeout=%s', e, timeout)
        except Exception as e:
            errors.append(str(e))
            if i == 0 and method == 'GET':
                timeout *= 2
    else:
        error_string = '<br />\n'.join(errors)
        if not error_string:
            logurl = 'https://appengine.google.com/logs?&app_id=%s' % os.environ['APPLICATION_ID']
            error_string = 'Internal Server Error. <p/>try <a href="javascript:window.location.reload(true);">refresh</a> or goto <a href="%s" target="_blank">appengine.google.com</a> for details' % logurl
        start_response('502 Bad Gateway', [('Content-Type', 'text/html; charset=utf-8')])
        yield message_html('502 Urlfetch Error', 'Python Urlfetch Error: %r' % method, error_string)
        raise StopIteration

    #logging.debug('url=%r response.status_code=%r response.headers=%r response.content[:1024]=%r', url, response.status_code, dict(response.headers), response.content[:1024])

    start_response('200 OK', [('Content-Type', 'image/gif')])

    status_code = int(response.status_code)
    data = response.content
    response_headers = response.headers
    content_type = response_headers.get('content-type', '')
    if status_code == 200 and maxsize and len(data) > maxsize and response_headers.get('accept-ranges', '').lower() == 'bytes' and int(response_headers.get('content-length', 0)):
        status_code = 206
        response_headers['Content-Range'] = 'bytes 0-%d/%d' % (maxsize-1, len(data))
        data = data[:maxsize]
    if status_code == 200 and 'content-encoding' not in response_headers and 512 < len(data) < URLFETCH_DEFLATE_MAXSIZE and content_type.startswith(('text/', 'application/json', 'application/javascript')):
        if 'gzip' in accept_encoding:
            response_headers['Content-Encoding'] = 'gzip'
            compressobj = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
            dataio = io.BytesIO()
            dataio.write('\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff')
            dataio.write(compressobj.compress(data))
            dataio.write(compressobj.flush())
            dataio.write(struct.pack('<LL', zlib.crc32(data) & 0xFFFFFFFFL, len(data) & 0xFFFFFFFFL))
            data = dataio.getvalue()
        elif 'deflate' in accept_encoding:
            response_headers['Content-Encoding'] = 'deflate'
            data = deflate(data)
    response_headers['Content-Length'] = str(len(data))
    if 'rc4' not in options:
        yield format_response(status_code, response_headers, '')
        yield data
    else:
        cipher = RC4Cipher(__password__)
        yield cipher.encrypt(format_response(status_code, response_headers, ''))
        yield cipher.encrypt(data)
