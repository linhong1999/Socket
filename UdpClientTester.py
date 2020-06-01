from socket import socket,AF_INET,SOCK_DGRAM
import os,asyncio
import threading
#服务端的ip地址
SERVER_IP = "127.0.0.1"
#服务端socket绑定的端口号
SERVER_PORT = 65531
BUFSIZE = 1024
ENCODING  = 'utf-8'
class Client:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_DGRAM) #SOCK_STREAM tcp  SOCK_DGRAM
        self.sock.bind(("", 65530))
        self.flag = 0
    def close(self):
        self.sock.close()

    def MsgGetter(self):
        while True:
            msg,addr = self.sock.recvfrom(BUFSIZE)
            print(">>>", msg.decode(ENCODING))
            print(self.flag)
            self.flag+=1
    def Msg(self,num):
        msg = None
        bytes_msg = None
        for i in range(num):
            msg = '(0{})据车辆互通的完善程度又可分为完全互'.format(str(i))
            bytes_msg = bytes(msg, ENCODING)
            yield bytes_msg

    async def Sender(self,msg):
        self.sock.sendto(msg, (SERVER_IP, SERVER_PORT))
    async def Getter(self):
        t1 = threading.Thread(target=client.MsgGetter)
        t1.start()

if __name__ == '__main__':
    client = Client()

    ioloop = asyncio.get_event_loop()
    tasks = []
    task = None
    task_10 = ioloop.create_task(client.Getter())
    tasks.append(task_10)
    for msg in client.Msg(100):
        task = client.Sender(msg)
        tasks.append(task)

    ioloop.run_until_complete(asyncio.wait(tasks))
    print('Tasks finish')
    ioloop.close()