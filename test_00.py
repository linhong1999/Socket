from socket import socket, AF_INET, SOCK_STREAM
import os
import threading
# 服务端的ip地址
SERVER_IP = "127.0.0.1"
# 服务端socket绑定的端口号
SERVER_PORT = 65530
BUFSIZE = 1024
ENCODING = 'utf-8'

class Client:
    def __init__(self, ip, port):
        self.sock = socket(AF_INET, SOCK_STREAM)  # SOCK_STREAM tcp  SOCK_DGRAM
        self.sock.connect((ip, port))

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
                    self.sock.send(bytes_msg)
            except:
                self.close()

    def MsgGetter(self):
        while True:
            msg = str(self.sock.recv(BUFSIZE), ENCODING)
            print(">>>", msg)
            # print('请输入要发送信息：')

if __name__ == '__main__':
    client = Client(SERVER_IP, SERVER_PORT)

    t0 = threading.Thread(target=client.MsgSender)
    t1 = threading.Thread(target=client.MsgGetter)

    t0.start()
    t1.start()
