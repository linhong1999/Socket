from socketserver import BaseRequestHandler, TCPServer,UDPServer,DatagramRequestHandler
import solver
import time,os
import threading,multiprocessing
#指定接收消息的客户端ip列表

encoding = 'utf-8'
CLIENT_IP_00 = "127.0.0.1"
CLIENT_IP_01 = "192.168.244.1"
CLIENT_IP_02 = "10.103.5.35"  #客户端公网ip  221.11.20.99
CLIENT_IP_03 = "10.99.4.22"  #客户端公网ip  221.11.20.99
CLIENT_IP_04 = "221.11.20.98"  #客户端公网ip  221.11.20.99
SERVER_IP = "127.0.0.1"   #服务器内网ip  172.24.27.53 192.168.244.129
# SERVER_IP = "10.99.4.22"
# SERVER_IP = "192.168.244.129"
# SERVER_IP = "172.17.0.2"
'''
SERVER_IP 为服务端内网ip 每次部署到新的服务器时得自行修改
target_clients 为过滤ip 当请求的ip属于其时，放行
'''
target_clients = [CLIENT_IP_00,CLIENT_IP_01,CLIENT_IP_02,CLIENT_IP_03,CLIENT_IP_04]

FUNC_MAP = {'2':"self.cpu_status_sender()" , '3':"self.pid_status_sender()",}

cpu_obj = solver.Cpu_Status()
conn_obj = solver.Pid_Status_Info()
grep_obj = solver.Grep_Pro_Status()
'''
FUNC_MAP 根据不同的指令执行不同的函数
cpu_obj 执行 cpu模块 conn_obj 执行进程模块 grep_obj 执行命令行模块
'''
# LOCK = threading.RLock()

CPU_PORT = 65530
PID_PORT = 65531
GREP_PORT = 65532
NWORKERS = 3
PORT_LIST = [CPU_PORT,PID_PORT,GREP_PORT]  #端口号列表
class Controler():
    def __init__(self):
        self.__button = True  #pause 或 start 开关
        self.listen_event = threading.Event() #event 线程阻塞与放行
        self.pid_flag = False
        self.cpu_flag = False
        self.lock = threading.RLock()  #GIL全局锁

    def setButton(self,boo):
        self.__button = boo

    def getButton(self):
        return self.__button

    def waitFunc(self):
        # print(self.pid_flag)
        # print(self.cpu_flag)
        # print(self.__button)
        '''
        此为了避免其中一个线程运行速度过快而导致另一个线程抢占不到资源
        故设置两个开关 当一个线程完成时 进入阻塞状态 当两个都完成时 释放
        并重新进入就绪状态 知道下一次阻塞
        对 pasue开关进行或操作，当线程都阻塞且开关为False时 会导致线程全部阻塞
        当开关为 True 释放，开关默认为True
        :return:
        '''
        if self.pid_flag and self.cpu_flag or self.__button:
            time.sleep(1)
            self.cpu_flag = False
            self.pid_flag = False
            self.listen_event.set()
            self.listen_event.clear()  #clear 之后可重新进入等待状态
        else:
            self.listen_event.wait()

button_contorler = Controler()
# button_contorler.run()
class EchoHandler(BaseRequestHandler):
    def handle(self):
        print('Get connection from', self.client_address)
        # print(id(button_contorler))
        for target_client in target_clients:
            if target_client in self.client_address:
            #    sender.Server_Sender(65535).return_switch_port(str(self.client_address[1]))  #让客户端监听端口
                self.msg_getter()
          #      self.msg_sender("自动回复：查看事务?[y/n]")
                break
    def msg_getter(self):
        '''
        当选择 状态4 即为命令行模式时 进入阻塞状态，等待客户端向服务端发出指令
        :return:
        '''
        while True:
            try:
                msg = self.request.recv(1024).decode(encoding)  # tcp
            except:
                print("Close connection from",self.client_address)
                return
            print('消息已收到-------',msg)
            # try:
            button_flag = msg.split()[0]
            if len(msg) == 1 and isinstance(eval(msg),int):
                print("选择了: ", msg)
                if msg in FUNC_MAP:
                    eval(FUNC_MAP[msg])
            elif button_flag == 'pause':
                self.msg_sender("暂停")
                button_contorler.setButton(False)
            elif button_flag == 'start' or button_flag == 'exit':
                self.msg_sender("开始")
                button_contorler.setButton(True)
                button_contorler.waitFunc()#释放
            else:
                self.grep_status_sender(msg)

    def msg_sender(self,str):
        # LOCK.acquire()
        try:
            ret_msg = bytes(str,encoding)
            self.request.send(ret_msg)  # tcp
            #    self.socket.sendto(ret_msg, self.client_address)  #udp
            print('发送成功')
            return True
        except:
            print("Close connection from",self.client_address)
            os._exit(0)
        # LOCK.release()

    def grep_status_sender(self,command):

        self.msg_sender(self.data_decode(grep_obj.runner(command)))

    def cpu_status_sender(self):
        while True:
            if button_contorler.getButton():
                button_contorler.cpu_flag = self.msg_sender(self.data_decode(cpu_obj.runner()))
                button_contorler.waitFunc()
            else:
                # print("wait")
                button_contorler.waitFunc()
            #    self.msg_sender(self.data_decode("wait...."))

    def pid_status_sender(self):
        while True:
            # start = time.time()
            if button_contorler.getButton():
                button_contorler.pid_flag = self.msg_sender(self.data_decode(conn_obj.runner()))
                button_contorler.waitFunc()
            else:
                # print("wait")
                # time.sleep(5)
                button_contorler.waitFunc()
            # print('at %1.1f seconds' % (time.time() - start))
            #    self.msg_sender(self.data_decode("wait...."))

    def data_decode(self,data):
        return str(data)

# class Multi_Process_Listener(threading.Thread):
class Multi_Process_Listener():
    def __init__(self,port,ip=''):
        # threading.Thread.__init__(self)
        self.serv = TCPServer((ip,port), EchoHandler)

    # def listener_starter(self):

        # t = threading.Thread(target=self.serv.serve_forever)
        # t.daemon = True
        # t.start()
        # self.serv.serve_forever()

    def run(self):
        self.serv.serve_forever()
        # self.listener_starter()

if __name__ == '__main__':
    print("服务端 listener start")
    thread_list = []
    for port in PORT_LIST:
        t = threading.Thread(target=Multi_Process_Listener(port,SERVER_IP).run)
        thread_list.append(t)
    for thread in thread_list:
        # thread.daemon = True
        thread.start()


    # Multi_Process_Listener(CPU_PORT, SERVER_IP).start()
    # Multi_Process_Listener(PID_PORT, SERVER_IP).start()
    # Multi_Process_Listener(GREP_PORT, SERVER_IP).start()


# import socketserver
#
# class Myserver(socketserver.BaseRequestHandler): # 定义的类名可以任意取，继承的父类固定格式
#
#     def handle(self):       # 必须要使用handle这个名字
#         print('listening_in_handle')
#         while 1:
#
#      #       from_client_data = self.request.recv(1024)[1].decode('utf-8')
#             from_client_data = self.request[0]
#             print(from_client_data)
#
#             # recv_msg = from_client_data[0]
#             # send_addr = from_client_data[1]
#             # print(recv_msg)
#
#             to_client_data = input('>>>').strip()
#             self.request.send(to_client_data.encode('utf-8'))
#
#
# if __name__ == '__main__':
#
#
#     ip_port = ('10.99.214.212',65533)
#     # socketserver.TCPServer.allow_reuse_address = True  # 允许端口重复使用
#     server = socketserver.ThreadingUDPServer(ip_port,Myserver)   # 固定格式
#     # 对 socketserver.ThreadingTCPServer 类实例化对象，将ip地址，端口号以及自己定义的类名传入，并返回一个对象
#     server.serve_forever()   # 固定格式，对象执行serve_forever方法，开启服务端
#     print('listening_begin')