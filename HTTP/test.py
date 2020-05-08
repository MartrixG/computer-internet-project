import re
import hashlib
import time
import os

s = b'GET http://jwes.hit.edu.cn/favicon.ico HTTP/1.1\r\nHost: jwes.hit.edu.cn\r\nProxy-Connection: keep-alive\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36\r\nAccept: image/webp,image/apng,image/*,*/*;q=0.8\r\nReferer: http://jwes.hit.edu.cn/\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7\r\nCookie: _ga=GA1.3.1177448943.1544780820; JSESSIONID=26D3F6917B08BD77A457BF905B00B6D6\r\n\r\n'
'''
b'GET http://jwes.hit.edu.cn/favicon.ico HTTP/1.1\r\n
Host: jwes.hit.edu.cn:80\r\n
Proxy-Connection: keep-alive\r\n
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36\r\n
Accept: image/webp,image/apng,image/*,*/*;q=0.8\r\n
Referer: http://jwes.hit.edu.cn/\r\n
Accept-Encoding: gzip, deflate\r\n
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7\r\n
Cookie: _ga=GA1.3.1177448943.1544780820; JSESSIONID=26D3F6917B08BD77A457BF905B00B6D6\r\n
\r\nadadad'
'''
'''
b'HTTP/1.1 200 OK\r\n
Server: Apache-Coyote/1.1\r\n
Pragma: no-cache\r\n
Expires: Thu, 01 Jan 1970 00:00:00 GMT\r\n
Cache-Control: no-cache\r\n
Cache-Control: no-store\r\n
Set-Cookie: JSESSIONID=C88F4E24FC6BFBDE5B388260E6E05919; Path=/\r\n
Content-Type: text/html;charset=UTF-8\r\n
Content-Language: en-US\r\n
Content-Length: 2589\r\n
Date: Wed, 30 Oct 2019 13:38:55 GMT'
'''
'''
b'HTTP/1.1 200 OK\r\n
Server: JSP3/2.0.14\r\n
Date: Wed, 30 Oct 2019 16:06:58 GMT\r\n
Content-Type: text/javascript\r\n
Content-Length: 728\r\n
Connection: keep-alive\r\n
Content-Encoding: gzip\r\n
ETag: "2693351355"\r\n
Last-Modified: Mon, 28 Sep 2015 08:06:48 GMT\r\n
Expires: Tue, 24 Dec 2019 16:33:40 GMT\r\n
Age: 26782398\r\n
Accept-Ranges: bytes\r\n
Cache-Control: max-age=31536000\r\n
Vary: Accept-Encoding\r\n
Ohc-Response-Time: 1 0 0 0 0 0\r\n
Ohc-Cache-HIT: hrbcm64 [4]'
'''
res = b'HTTP/1.1 200 OK\r\nServer: JSP3/2.0.14\r\nDate: Wed, 30 Oct 2019 16:06:58 GMT\r\nContent-Type: text/javascript\r\nContent-Length: 728\r\nConnection: keep-alive\r\nContent-Encoding: gzip\r\nETag: "2693351355"\r\nLast-Modified: Mon, 28 Sep 2015 08:06:48 GMT\r\nExpires: Tue, 24 Dec 2019 16:33:40 GMT\r\nAge: 26782398\r\nAccept-Ranges: bytes\r\nCache-Control: max-age=31536000\r\nVary: Accept-Encoding\r\nOhc-Response-Time: 1 0 0 0 0 0\r\nOhc-Cache-HIT: hrbcm64 [4]'
def splitHeader(string):
    return string.split(b'\r\n\r\n')[0]
#print(splitHeader(s))
def getHeader(string, name):
    decode = string.decode('UTF-8')
    header = re.compile(name+r'.*', re.IGNORECASE)
    match = header.search(decode)
    if match:
        head = match.group()
        replace = re.compile(r'\r')
        head = replace.sub('', head)
        return head.encode('UTF-8')
    else:
        return None
url = getHeader(s, "get").split(b' ')[1]
#print(rawhost)
def transHost(string):
    header = string.decode('UTF-8')
    groups = header.split(":")
    host = groups[1].encode('UTF-8')
    if len(groups) > 2:
        port = groups[2].encode('UTF-8')
    else:
        port = "80".encode('UTF-8')
    return host, port

cache = {}
path = '计算机网络\cache'
def writeCache(url, timestamp, body):
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    cache[url] = timestamp
    file = open('计算机网络\cache\dict.txt', 'w')
    for key in cache:
        file.write(key+':'+cache[key])
    file.close()
    file = open('计算机网络\cache\\'+url, 'wb')
    file.write(body)
def loadCache():
    file = open(path+'\dict.txt', 'r')
    line = file.readline()
    while line:
        line = line.split(':')
        cache[line[0]] = line[1]
        line = file.readline()
def checkCache(url):
    hl = hashlib.md5()
    hl.update(url)
    if cache.__contains__(url):
        return True
    else:
        return False
def loadbody(url):
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    for entry in os.listdir('计算机网络\cache'):
        if(entry == url):
            file = open('计算机网络\cache\\'+entry, 'rb')
loadCache()
t = getHeader(res, 'Last-Modified').split(b':')[1].decode('UTF-8')
if checkCache(url):
    print('Hit')
else:
    writeCache(url, t, b'nmhnmsl')
loadbody(url)
modify = '\r\n123jlk123'+'fffff'+'\r\n\r\n'
ss = b'asdas\r\nasdas\r\n\r\n'
newrequest = ss.replace(b'\r\n\r\n', modify.encode('UTF-8'))
print(newrequest)
#print(splitHeader(rawhost))
