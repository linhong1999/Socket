import threading
import sys
import socket
import asyncio
encoding = "utf-8"
SERVER_IP_00 = "172.17.0.2"   #服务器公网ip 49.234.197.31
SERVER_IP_01 = "127.0.0.1"
LISTEN_MAP = {
    "1": "127.0.0.1", "2" : "49.234.220.238" , "3" : "192.168.244.129"
}
LISTEN_LIST = [key +": " + value for key,value in LISTEN_MAP.items()]
CLIENT_IP = "127.0.0.1" #10.99.214.212  #本地 内网IP
BUFSIZE = 8192

class Starter(threading.Thread):
    def __init__(self,port,flag,server_ip):
        threading.Thread.__init__(self)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_STREAM tcp  SOCK_DGRAM
        self.sock.connect((server_ip, port))
        self.flag = bytes(flag, encoding)

    def grep_command_runner(self):
        # flag = True
        while flag:
            msg = input(">>>")
            if msg == 'exit':
                self.sock.send(bytes(msg, encoding))
                self.sock.close()
                # flag = False
                return
            self.sock.send(bytes(msg, encoding))
            try:
                recv_data = self.sock.recv(BUFSIZE)
                recv_msg = bytes.decode(recv_data, encoding)
                if recv_data:
                    print("===>从 {}收到了 {}".format(self.sock.getpeername(), recv_msg))
                else:
                    pass
                #    time.sleep(1)
            except:
                print("异常关闭")
                self.sock.close()

    def run(self):
      #  reciver.listener_start()    #先打开监听 再 发送消息等待接收
        self.sock.send(self.flag)
        try:
            while True:
                recv_data = self.sock.recv(BUFSIZE)
                recv_msg = bytes.decode(recv_data, encoding)
                if recv_data:
                    print("===>从 {}收到了 {}".format(self.sock.getpeername(),recv_msg))
                    print()
                else:
                    pass
            #    time.sleep(1)
        except:
            print("异常关闭")
            self.sock.close()

async def task_00():
    Starter(65530, "2", arg_1).start()

async def task_01():
    Starter(65531, "3", arg_1).start()

if __name__ == "__main__":
    arg_0 = sys.argv[1]
    arg_1 = sys.argv[2]
    # arg_0 = "3"
    # arg_1 = "182.92.76.22"
    if arg_0 == "4":
        while True:
            print("\n".join([item for item in LISTEN_LIST]))
            flag = input("请选择:")
            while True:
                try:
                    ip = LISTEN_MAP[flag]
                    Starter(65532,'',ip).grep_command_runner()
                    break
                except:
                    print("输入有误，重试")
                    continue

    ioloop = asyncio.get_event_loop()
    tasks = {
        ioloop.create_task(task_00()),
        ioloop.create_task(task_01())
    }
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()

    # Starter(65530,"2","192.168.244.129").start()
    #  Starter(65530,"2",SERVER_IP_00).start()
    # Starter(65531,"3","192.168.244.129").start()

    #  Starter(65531,"3",SERVER_IP_00).start()

    # Starter(65531,"2",SERVER_IP_01).start()
    # Starter(65530,"3",SERVER_IP_01).start()
