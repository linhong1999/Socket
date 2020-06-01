import threading
import socket
import time

encoding = 'utf-8'
BUFSIZE = 1024
CLIENT_IP = "127.0.0.1" #10.99.214.212  192.168.244.129

class Reader(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
       try:
            while True:

                recv_data = self.client.recv(BUFSIZE)
                print('ccccccccccccccccccccc')
                if recv_data:
                    recv_msg = bytes.decode(recv_data, encoding)
                    print(recv_msg)
                    print("从 {}收到了 {}".format(self.client.getpeername(),recv_msg))
                else:
                    break

            #    print("close:", self.client.getpeername())
       except:
           print("\nclose:", self.client.getpeername())

    # def readline(self):
    #     print('执行了')
    #     rec = eval("telnet 111.230.200.15 8000")
    #     if rec:
    #         string = bytes.decode(rec, encoding)
    #         if len(string) > 2:
    #             string = string[0:-2]
    #         else:
    #             string = ' '
    #     else:
    #         string = False
    #     return string

class Listener(threading.Thread):
    def __init__(self,port):
        threading.Thread.__init__(self)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((CLIENT_IP, port))
        # self.sock.listen(0)

    def run(self):
        print("本地端 listener start ",self.port)
        while True:
            self.sock.recv(BUFSIZE)
            time.sleep(10)
            # recv_data = self.sock.recvfrom(BUFSIZE)
            # recv_msg = recv_data[0]
            # send_addr = recv_data[1]
            #
            # print("收到了{}{}".format(str(send_addr),recv_msg.decode(encoding)))
            # print('vvvvvvvvvvvvvvvvvvvvvvvv')
            # client,addr = self.sock.accept()
            # print(addr)
            # print(str(client.recv(8192),encoding="utf-8"))
            #
            # print('vvvvvvvvvvvvvvvvvvvvvvvsssssssss')

         #   Reader(client).start()
            # cltadd = cltadd
            # print("accept a connect")

# def listener_start(port0,port1):
#     Listener(65530).start()
#     Listener(65531).start()



if __name__ == '__main__':
    # listener_start()
    lst  = Listener(65530)   # create a listen thread
    lst.start()