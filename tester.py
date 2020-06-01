import time
from socket import socket,AF_INET,SOCK_DGRAM
import os
import threading
#服务端的ip地址
# server_ip = "192.168.244.129"    #49.234.197.31
# SERVER_IP = "49.234.220.238"
SERVER_IP = "127.0.0.1"
#服务端socket绑定的端口号
SERVER_PORT = 65530
BUFSIZE = 1024
ENCODING  = 'utf-8'
class Client:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_DGRAM) #SOCK_STREAM tcp  SOCK_DGRAM
        self.sock.bind(("", 65531))

    def close(self):
        self.sock.close()

    def MsgSender(self):
        print('请输入要发送信息：')
        while True:
            try:
                msg = input()
                if msg == 'exit':
                    os._exit(0)
                if msg != "":
                    bytes_msg = bytes(msg, ENCODING)
                    self.sock.sendto(bytes_msg,(SERVER_IP,SERVER_PORT))
                    # msg, addr = self.sock.recvfrom(BUFSIZE)
            except:
                self.close()

    def MsgGetter(self):
        while True:
            msg,addr = self.sock.recvfrom(BUFSIZE)
            print(">>>", msg.decode(ENCODING))
            print('请输入要发送信息：')

if __name__ == '__main__':
    client = Client()
    t0 = threading.Thread(target=client.MsgSender)
    t1 = threading.Thread(target=client.MsgGetter)

    t0.start()
    t1.start()
