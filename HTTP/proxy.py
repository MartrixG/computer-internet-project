import socket
import sys
import threading
import time
import traceback
import os
import re
import hashlib

MAX_HEADER = 4096
RECV_SIZE = 512

ban_list = [
    b'jwes.hit.edu.cn'
]  # 网站过滤列表

change_list = {
    b'www.hit.edu.cn': b'studyathit.hit.edu.cn'
}  # 网站引导字典

user_list = [
    '127.0.0.1'
]  # 用户过滤列表

c = {}


def getHeader(string, name):  # 从请求头中提取关键字
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


def transHost(raw_host):  # 将请求头中的host和port分隔开
    header = raw_host.decode('UTF-8', 'ignore')
    groups = header.split(":")
    host = groups[1].encode('UTF-8')
    if len(groups) > 2:
        port = int(groups[2])
    else:
        port = 80
    return host, port


def splitHeader(string):  # 获取请求头
    return string.split(b'\r\n\r\n')[0]


def recvBody(conn, base, size):  # 接收剩余的数据内容
    if size == -1:  # 没有写明长度，按照报告中的方法确定结尾
        while(base[-7:] != b'\r\n0\r\n\r\n'):
            base += conn.recv(RECV_SIZE)
    else:
        while len(base) < size:  # 如果写明了长度，读取到规定的长度
            base += conn.recv(RECV_SIZE)
    return base


def checkCache(cache, url):  # 检查该url是否被缓存
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    if cache.__contains__(url):
        return True
    else:
        return False


def writeCache(cache, url, timestamp, body):  # 将缓存写入文件夹并且在字典中添加md5编码和时间
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


def loadbody(cache, url):  # 从文件夹中读取缓存的内容
    hl = hashlib.md5()
    hl.update(url)
    url = hl.hexdigest()
    for entry in os.listdir('计算机网络\HTTP\cache'):
        if(entry == url):
            file = open('计算机网络\HTTP\cache\\'+entry, 'rb')
            return file.read()


def thread_proxy(client, addr, cache, banlist, changelist, userlist):  # 代理线程
    thread_name = threading.currentThread().name
    # 监测是否ban IP地址
    if userlist != None:
        if userlist.count(addr[0]) != 0:
            print("%sThis client is banned!" % (thread_name))
            client.close()
            return
    # 尝试接受客户端发送的requset
    try:
        request = client.recv(MAX_HEADER)
    except:  # 如果超时输出错误信息
        print("%sTime out!" % (thread_name))
        client.close()
        return
    # 获得初始的host
    raw_host = getHeader(request, "Host").replace(b' ', b'')
    url = getHeader(request, 'get').split(b' ')[1]

    if not raw_host:  # 如果提取不到host输出错误信息
        print("%sHost request error%s" % (thread_name, str(addr)))
        client.close()
        return

    host, port = transHost(raw_host)
    print("%sGET:%s:%s" % (thread_name, url, str(port)))

    # 钓鱼
    if changelist != None:
        if changelist.__contains__(host):
            host = changelist[host]  # 修改host
            print("%sHost has change to %s" % (thread_name, host))
    # 禁止访问的host
    if banlist != None:
        if banlist.count(host) != 0:
            print("%sThis host is banned" % (thread_name))
            client.close()
            return
    # 建立到服务器的连接
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.settimeout(10)
    try:
        server.connect((host, port))
    except socket.timeout:  # 如果超时输出错误信息
        print("%sTime out!" % (thread_name))
        server.close()
        client.close()
        return

    # 检查缓存
    if checkCache(cache, url):
        # 修改request 监测是否变化
        url_md5 = hashlib.md5()
        url_md5.update(url)
        url_md5 = url_md5.hexdigest()
        modify = '\r\nIf-Modified-Since:'+cache[url_md5]+'\r\n\r\n'
        newrequest = request
        newrequest = newrequest.replace(
            b'\r\n\r\n', modify.encode('UTF-8'))  # 修改request
        server.sendall(newrequest)
        response = server.recv(MAX_HEADER)
        responseHeader = splitHeader(response)
        flag = getHeader(responseHeader, 'HTTP/1.1').split(b' ')[1]
        if flag == b'304':  # 如果返回了304，直接读取缓存，然后结束
            print("%sCache hit!!" % (thread_name))
            response = loadbody(cache, url)
            client.sendall(response)

            server.close()
            client.close()
            return

    # 未命中发送未修改的request
    server.sendall(request)

    response = server.recv(RECV_SIZE)
    responseHeader = splitHeader(response)

    if len(responseHeader) < len(response) - 4:  # 如果响应头长度和接收长度不同，说明没有接受完全部数据
        content_size = getHeader(responseHeader, 'content-length')
        if content_size:
            size = int(content_size.split(b':')[1]) + 4 + len(responseHeader)
        else:
            size = -1
        response = recvBody(server, response, size)
    client.sendall(response)  # 转发数据
    # 写入缓存
    time = getHeader(responseHeader, 'Last-Modified')
    if time != None:
        # 如果含有Last-Modified说明可被缓存
        time = time.split(b': ')[1].decode('UTF-8')
        writeCache(cache, url, time, response)

    server.close()
    client.close()


def thread_server(myserver):
    while True:
        conn, addr = myserver.accept()
        conn.settimeout(10)
        thread_p = threading.Thread(target=thread_proxy, args=(
            conn, addr, c, None, change_list, None))
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


def loadCache():  # 从文件中建立起字典
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
