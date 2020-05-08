<center>哈尔滨工业大学计算机科学与技术学院</center>
<center style="font-size:30px">实验报告 </center><br></br>
<center>课程名称： 计算机网络</center>
<center>课程类型： 必修</center>
<center>实验题目： HTTP 代理服务器的设计与实现</center><br/>
<center>学号：1171000405</center>
<center>姓名：许天骁</center>
<div STYLE="page-break-after: always;"></div>

#### 一、实验目的
&ensp;&ensp;熟悉并掌握 Socket 网络编程的过程与技术；深入理解 HTTP 协议，掌握 HTTP 代理服务器的基本工作原理；掌握 HTTP 代理服务器设计与编程实现的基本技能。

#### 二、实验要求及实验环境

##### 实验内容
1. 设计并实现一个基本 HTTP 代理服务器。要求在指定端口接收来自客户的 HTTP 请求并且根据其中的 URL 地址访问该地址所指向的 HTTP 服务器（原服务器），接收 HTTP 服务器的响应报文，并将响应报文转发给对应的客户进行浏览。
2. 设计并实现一个支持 Cache 功能的 HTTP 代理服务器。要求能缓存原服务器响应的对象，并能够通过修改请求报文，向原服务器确认缓存对象是否是最新版本。
3. 扩展 HTTP 代理服务器，支持如下功能：
a) 网站过滤：允许/不允许访问某些网站；
b) 用户过滤：支持/不支持某些用户访问外部网站；
c) 网站引导：将用户对某个网站的访问引导至一个模拟网站（钓鱼）。
##### 实验环境
1. 硬件环境：X64CPU; 4.0Ghz; 16G RAM
2. 软件环境：Windows 64位
3. 开发环境：Python 3.6.8(64位); Visual Stuio Code

#### 三、实验过程及结果
##### 建立服务器
   首先使用Python的socket包建立套接字连接，并且将其和固定的IP地址（127.0.0.1表示本机）和端口号（8000）绑定。然后开启对这个端口号的请求的监听。当获取到（Accept）请求时，创建新的线程用于对请求进行处理。打开浏览器使用代理选项，将所有的浏览器请求转发到创建的服务器中。在这个过程中，浏览器是客户端。
##### 处理浏览器的请求
1. 分割请求头获取信息
   当建立起处理请求线程时，需要传入对应的套接字、IP地址、端口号这些参数。使用套接字的recv函数获取一部分请求信息。利用 '\r\n\r\n' 作为分隔符，将头部信息和数据部分进行分割。使用正则表达式，获取到请求的目标主机（host）、端口号（port）、请求的资源地址（URL）。
2. 建立服务器和目标主机的连接
   此时当前的线程作为一个客户端，建立和目标主机服务器的连接。使用套接字的connect方法和目标服务器连接。然后将在第1部分获取到的所有的请求，转发给目标服务器。
3. 处理服务器响应
   首先接收一部分数据，利用 '\r\n\r\n' 进行响应头的分割。提取content-length参数的信息。这个参数信息表示响应头和响应数据部分的大小总和。然后循环接收服务器的响应数据，直到长度满足。若没有content-length信息，则利用 '\r\n0\r\n\r\n' 作为数据部分的结尾符。
4. 转发数据
   将在第4部分获取到的所有报文信息转发给当前线程的客户端，完成一个实验要求的第一部分

##### 支持缓存（cache）的HTTP代理服务器
缓存功能支持代理服务器可以缓存原服务器响应的对象，并且能够修改请求报文，向服务器确认是否是最新版本。
###### 缓存文件夹和缓存文件字典
1. 缓存文件夹按照缓存文件的URL地址的MD5编码进行命名，内容是文件的实际内容。
2. 缓存文件字典存储着文件名和上一次修改时间的对应关系，用于向服务器主机确定文件是否发生了修改。
###### 缓存检查和缓存写入
1. 对于任何一个URL请求，将URL链接进行MD5加密后，检车缓存文件字典。如果存在，向请求的HOST发送带有'If-Modified-Since'语句的请求报文。语句后半部分是缓存文件字典中储存的时间。如果服务器主机发送的响应报文是304表示该文件没有被修改过，可以直接读取缓存文件夹，将内容提取出来，发送给客户端。
2. 若该URL没有被缓存在字典中，或者被缓存但是发生了修改，那么正常进行数据的读取。读取完完整的数据后，检查响应头是否含有 'Last-Modified' 字段。如果有，将其缓存在缓存文件夹中，并且将MD5码和时间存入缓存文件字典中。
##### 扩展HTTP代理服务器
1. 网站过滤
   在建立线程时添加网站过滤列表参数，在获取到了访问主机的HOST时，检查当前的HOST是否存在于列表之中。如果存在直接关闭连接。
2. 用户过滤
   在建立线程时添加用户过滤列表参数，检查传入的IP地址参数，如果IP地址存在于用户过滤列表中，直接关闭连接。
3. 网站引导
   在建立线程时添加网站引导字典参数。对于任何一个请求的HOST，在网站引导字典中检查是否存在当前HOST关键字。如果存在，将HOST转换为对应的value值，完成网站引导。
##### 实验结果
基础功能：
<img src="./omega.png">开启网站代理
<img src="./HIT.png">访问 'www.hit.edu.cn'
<img src="./jwes.png">访问 'jwes.hit.edu.cn'
缓存功能：
<img src="./cache_hit.png">强制刷新 'jwes.hit.edu.cn' 页面后，可以看到申请访问相同的元素后，发生了缓存命中
网站过滤：
<img src="./ban_jwes.png">
<img src="./banjwes.png">
添加了网站过滤后，'jwes.hit.edu.cn' 的页面被禁止访问了
用户过滤：
<img src="./user.png">
添加了用户过滤后，客户端为发送请求就已经被代理服务器断开了连接
网站引导：
<img src="./change_hit.png">
<img src="./changehit.png">
添加了网站引导后，可以看到访问了 'www.hit.edu.cn' 后实际跳转到了 'studyathit.hit.edu.cn' 

#### 四、实验心得
1. 通过这次实验，我掌握了Python环境下的socket编程，学会了查看HTTP请求的报文头，和响应头。了解了报文的默认格式。
2. 了解了Python多线程的使用。

#### 五、源代码
```python
import socket, sys, threading, time, traceback, os
import re
import hashlib

MAX_HEADER = 4096
RECV_SIZE = 512

ban_list = [
    b'jwes.hit.edu.cn'
]#网站过滤列表

change_list = {
    b'www.hit.edu.cn' : b'studyathit.hit.edu.cn'
}#网站引导字典

user_list = [
    '127.0.0.1'
]#用户过滤列表

c = {}

def getHeader(string, name):#从请求头中提取关键字
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

def transHost(raw_host):#将请求头中的host和port分隔开
    header = raw_host.decode('UTF-8', 'ignore')
    groups = header.split(":")
    host = groups[1].encode('UTF-8')
    if len(groups) > 2:
        port = int(groups[2])
    else:
        port = 80
    return host, port

def splitHeader(string):#获取请求头
    return string.split(b'\r\n\r\n')[0]

def recvBody(conn, base, size):#接收剩余的数据内容
    if size == -1:#没有写明长度，按照报告中的方法确定结尾
        while(base[-7:] != b'\r\n0\r\n\r\n'):
            base += conn.recv(RECV_SIZE)
    else:
        while len(base) < size:#如果写明了长度，读取到规定的长度
            base += conn.recv(RECV_SIZE)
    return base

def checkCache(cache, url):#检查该url是否被缓存
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    if cache.__contains__(url):
        return True
    else:
        return False

def writeCache(cache, url, timestamp, body):#将缓存写入文件夹并且在字典中添加md5编码和时间
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    cache[url] = timestamp
    file = open('计算机网络\HTTP\dict.txt', 'a')
    file.write(url+'::'+timestamp+'\n')
    file.close()
    file = open('计算机网络\HTTP\cache\\'+url, 'wb')
    file.write(body)
    file.close()

def loadbody(cache, url):#从文件夹中读取缓存的内容
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    for entry in os.listdir('计算机网络\HTTP\cache'):
        if(entry == url):
            file = open('计算机网络\HTTP\cache\\'+entry, 'rb')
            return file.read()


def thread_proxy(client, addr, cache, banlist, changelist, userlist):#代理线程
    thread_name = threading.currentThread().name
    #监测是否ban IP地址
    if userlist != None:
        if userlist.count(addr[0]) != 0:
            print("%sThis client is banned!"%(thread_name))
            client.close()
            return
    #尝试接受客户端发送的requset
    try:
        request = client.recv(MAX_HEADER)
    except:#如果超时输出错误信息
        print("%sTime out!"%(thread_name))
        client.close()
        return
    #获得初始的host
    raw_host = getHeader(request, "Host").replace(b' ', b'')
    url = getHeader(request, 'get').split(b' ')[1]
    
    if not raw_host:#如果提取不到host输出错误信息
        print("%sHost request error%s"%(thread_name, str(addr)))
        client.close()
        return
    
    host, port = transHost(raw_host)
    print("%sGET:%s:%s"%(thread_name, url, str(port)))

    #钓鱼
    if changelist != None:
        if changelist.__contains__(host):
            host = changelist[host]#修改host
            print("%sHost has change to %s"%(thread_name, host))
    #禁止访问的host
    if banlist != None:
        if banlist.count(host) != 0:
            print("%sThis host is banned"%(thread_name))
            client.close()
            return
    #建立到服务器的连接
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(10)
    try:
        server.connect((host, port))
    except socket.timeout:#如果超时输出错误信息
        print("%sTime out!"%(thread_name))
        server.close()
        client.close()
        return
    
    #检查缓存
    if checkCache(cache, url):
        #修改request 监测是否变化
        url_md5 = hashlib.md5()
        url_md5.update(url)
        url_md5 = url_md5.hexdigest()
        modify = '\r\nIf-Modified-Since:'+cache[url_md5]+'\r\n\r\n'
        newrequest = request
        newrequest = newrequest.replace(b'\r\n\r\n', modify.encode('UTF-8'))#修改request
        server.sendall(newrequest)
        response = server.recv(MAX_HEADER)
        responseHeader = splitHeader(response)
        flag = getHeader(responseHeader, 'HTTP/1.1').split(b' ')[1]
        if flag == b'304':#如果返回了304，直接读取缓存，然后结束
            print("%sCache hit!!"%(thread_name))
            response = loadbody(cache, url)
            client.sendall(response)

            server.close()
            client.close()
            return
    
    #未命中发送未修改的request
    server.sendall(request)

    response = server.recv(RECV_SIZE)
    responseHeader = splitHeader(response)

    if len(responseHeader) < len(response) - 4:#如果响应头长度和接收长度不同，说明没有接受完全部数据
        content_size = getHeader(responseHeader, 'content-length')
        if content_size:
            size = int(content_size.split(b':')[1]) + 4 + len(responseHeader)
        else:
            size = -1
        response = recvBody(server, response, size)
    client.sendall(response)#转发数据
    #写入缓存
    time = getHeader(responseHeader, 'Last-Modified')
    if time != None:
        #如果含有Last-Modified说明可被缓存
        time = time.split(b': ')[1].decode('UTF-8')
        writeCache(cache, url, time, response)

    server.close()
    client.close()

def thread_server(myserver):
    while True:
        conn, addr = myserver.accept()
        conn.settimeout(10)
        thread_p = threading.Thread(target=thread_proxy, args=(conn, addr, c, None, change_list, None))
        thread_p.setDaemon(True)
        thread_p.start()

def main(port=8000):
    try:
        myserver = socket.socket()
        myserver.bind(('127.0.0.1', port))
        myserver.listen(1024)
        thread_s = threading.Thread(target=thread_server, args=(myserver,))
        thread_s.setDaemon(True)
        thread_s.start()
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("sys exit")
    finally:
        myserver.close()

def loadCache():#从文件中建立起字典
    file = open('计算机网络\HTTP\dict.txt', 'r')
    line = file.readline()
    while line:
        line = line.split('::')
        c[line[0]] = line[1][:-1]
        line = file.readline()
# 命令入口
if __name__ == '__main__':
    try:
        loadCache()
        print("Start proxy...")
        main()
    except Exception as e:
        print("error exit")
        traceback.print_exc()
    finally:
        print("end server")
    sys.exit(0)