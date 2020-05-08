import socket
import random
import string
import time
from threading import Lock, Thread
import traceback

S1_ADDR = ('127.0.0.1', 8000)
S2_ADDR = ('127.0.0.1', 8001)

DATA_LENGTH = 200
CHUNK_SIZE = 10
WINDOW = 5
RECV_SIZE = 1024
TIMEOUT = 0.5
MAX_SIZE = 16
TIME_OUT_RATE = 0.1
PACKET_LOSS_RATE = 0.1
EOF = bytes([0]) * CHUNK_SIZE
base = 0
timer = 0
lock = Lock()


def make_data(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode('utf-8')


def make_file():
    with open('计算机网络\GBN\image\send_image.jpg', 'rb') as f:
        image_data = f.read()
    return image_data


def make_ack(num):
    return (num).to_bytes(1, byteorder='little')


def divide_data(base_data, chunk_size):
    length = len(base_data)
    re = []
    i = 0
    while i * chunk_size < length:
        if i + chunk_size < length:
            re.append((i % MAX_SIZE).to_bytes(1, byteorder='little') +
                      base_data[i * chunk_size:i * chunk_size + chunk_size])
            i += 1
        else:
            re.append((i % MAX_SIZE).to_bytes(
                1, byteorder='little') + base_data[i:])
            break
    eof = (i % MAX_SIZE).to_bytes(
        1, byteorder='little') + bytes([0]) * chunk_size
    re.append(eof)
    return re


def get_data(sdata):
    num = int.from_bytes(sdata[:1], byteorder='little')
    if len(sdata) == 1:
        return (num, None)
    else:
        data = sdata[1:]
    return (num, data)


def send(conn, data, tar):
    if random.random() >= PACKET_LOSS_RATE:
        conn.sendto(data, tar)
    else:
        print('dropped.')
    return


def sendto(conn, rawdata, tar):
    data_piece = divide_data(rawdata, CHUNK_SIZE)
    global base
    global timer
    next_seq_num = 0
    tot_num = len(data_piece) - 1
    win = WINDOW
    next_num = 0
    while True:
        lock.acquire()
        if (next_seq_num - base + 1 + MAX_SIZE) % MAX_SIZE < win and next_num <= tot_num:
            send_thread = Thread(target=send, args=(
                conn, data_piece[next_num], tar))
            if(random.random() <= TIME_OUT_RATE):
                time.sleep(1.5)
            print('Send data%s:%s' % (next_seq_num, data_piece[next_num]))
            send_thread.start()
            if base == next_seq_num:
                timer = time.perf_counter()
            next_seq_num = (next_seq_num + 1) % MAX_SIZE
            next_num += 1
        if time.perf_counter() - timer > TIMEOUT:
            timer = time.perf_counter()
            gap = (next_seq_num - base + MAX_SIZE) % MAX_SIZE
            base_num = next_num - gap
            for i in range(gap):
                send_thread = Thread(target=send, args=(
                    conn, data_piece[base_num + i], tar))
                if(random.random() <= TIME_OUT_RATE):
                    time.sleep(1.5)
                print('Send data%s:%s' % ((base_num + i) %
                                          MAX_SIZE, data_piece[base_num + i]))
                send_thread.start()
        if next_num == tot_num + 1 and (next_seq_num - base + MAX_SIZE) % MAX_SIZE == 2:
            lock.release()
            break
        lock.release()
        time.sleep(0.05)
    print('Send end.')


def recvfrom(conn, size, tar):
    global base
    global timer
    expect_seq_num = 0
    re = b''
    while True:
        rawdata, addr = conn.recvfrom(size)
        num, data = get_data(rawdata)
        if data == EOF:
            # print(re)
            with open('计算机网络\GBN\image\\recv_image.jpg', 'wb') as f:
                f.write(re)
        elif data == None:
            print('Recive ACK%d' % (num))
            ack = num
            lock.acquire()
            if (ack - base + 1 + MAX_SIZE) % MAX_SIZE <= WINDOW:
                base = ack
                timer = time.perf_counter()
            lock.release()
        else:
            print('Recive data:%s' % (data))
            if num == expect_seq_num:
                expect_seq_num = (expect_seq_num + 1) % MAX_SIZE
                re += data
            ack = make_ack((expect_seq_num + MAX_SIZE - 1) % MAX_SIZE)
            send_thread = Thread(target=send, args=(conn, ack, tar))
            send_thread.start()
            print('send ACK%d' % (int.from_bytes(ack, byteorder='little')))
        time.sleep(0.05)


def listen(conn, tar_addr):
    recv_th = Thread(target=recvfrom, args=(conn, RECV_SIZE, tar_addr))
    recv_th.start()
    while True:
        arg = input()
        if arg == 'time':
            now_time = time.time()
            time_local = time.localtime(now_time)
            data = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            print(data)
            data = data.encode('utf-8')
            send_th = Thread(target=sendto, args=(conn, data, tar_addr))
            send_th.start()
        if arg == 'quit':
            break
        if arg == 'testgbn':
            data = make_data(DATA_LENGTH)
            print(data.decode('utf-8'))
            send_th = Thread(target=sendto, args=(conn, data, tar_addr))
            send_th.start()
        if arg == 'testfile':
            data = make_file()
            send_th = Thread(target=sendto, args=(conn, data, tar_addr))
            send_th.start()
        time.sleep(0.5)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(S1_ADDR)
        print(S1_ADDR)
        listen(s, S2_ADDR)
    except Exception:
        s.bind(S2_ADDR)
        print(S2_ADDR)
        listen(s, S1_ADDR)
    except KeyboardInterrupt:
        print('sys exit')
    finally:
        s.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("error exit")
        traceback.print_exc()
    finally:
        print('end server')
