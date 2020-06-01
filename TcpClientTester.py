from socket import socket, AF_INET, SOCK_STREAM
import asyncio
import threading

# 服务端的ip地址
# SERVER_IP = "49.234.220.238"
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
    def Msg(self,num):
        msg = None
        for i in range(num):
            msg = '(0{})据车辆互通的完善程度又可分为完全互'.format(str(i))
            bytes_msg = bytes(msg, ENCODING)
            yield bytes_msg

    async def Sender(self, msg):
        self.sock.send(msg)

    def MsgGetter(self):
        while True:
            msg = str(self.sock.recv(BUFSIZE), ENCODING)
            print(">>>", msg)
            # print('请输入要发送信息：')

    async def Getter(self):
        t1 = threading.Thread(target=client.MsgGetter)
        t1.start()

if __name__ == '__main__':
    client = Client(SERVER_IP, SERVER_PORT)
    ioloop = asyncio.get_event_loop()
    tasks = []
    task = None
    task_10 = ioloop.create_task(client.Getter())
    tasks.append(task_10)
    for msg in client.Msg(10):
        task = client.Sender(msg)
        tasks.append(task)

    ioloop.run_until_complete(asyncio.wait(tasks))
    print('Tasks finish')
    ioloop.close()
