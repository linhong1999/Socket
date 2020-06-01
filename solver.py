import socket
import threading
import os,asyncio,signal
import psutil
import re
import time,datetime

IP = '127.0.0.1'
ports = [21]  #获取 端口号
SVMEN = {}   #内存统计数据
SSWAP = {} #swap的统计数据
CPU_STATUS = []

PROCESS_STATUS = {'PID':0,'PROCESS_NAME':'','CPU_PERCENT':0,'USED_MEMORY':0,'PROCESS_NUM':0}
SCONN_STATUS = {'LISTEN':0,'ESTABLISHED':0,'TIME_WAIT':0,'CLOSE_WAIT':0,'LAST_ACK':0,'SYN_SENT':0,'NONE':0,'FIN_WAIT2':0}#连接状态


PORT_PID = {} # 一个进程 可能占用多个端口 故为动态字典

#连接情况
CONN_STATUS = {'LISTEN':0,'ESTABLISHED':0,'TIME_WAIT':0,'CLOSE_WAIT':0,'LAST_ACK':0,'SYN_SENT':0,'NONE':0,'FIN_WAIT2':0}#连接状态
CONN_LIST = []
PID_PORT_DICT = {}  #进程号 端口 字典
# EXPECT_LADDR = ['::','::1','192.168.244.1','192.168.230.1']  #剔除的ip
EXPECT_LADDR = ['::','::1','192.168.244.1']  #由于 两个虚拟机监听的端口一样，这里只取一个
EXPECT_PORT_PID_DIC = {}  #剔除的端口号

# METHOD_MAP = {
#     '1':"get_cpu_core_num",'2':"cup_status_runner",'3':"filter_conn_data",'4':"process_status",
# }
COMMAND_MAP = {
    "get name -p ":".name()","get status -p ":".status()",
    "get memory percent -p ": ".memory_percent()","get threads -p ": ".num_threads()",
    "get create time -p ": ".create_time()","kill -p -l ":"os.kill({},signal.SIGKILL)",
    "kill -p -w ":"os.popen('taskkill /pid {} -t -f')",
}
'''
由于 获取 CPU 状态 比 获取 进程状态  慢得多 故 CPU 那三个函数 改为协程
用协程前 每次 1s 用之后 0s
'''

# 1. 逻辑CPU核数
# 2. CPU状态
# 3. 连接情况
# 4. 进程状态
class Data_Dict_Init():
    def __init__(self):
        self.CONN_STATUS = {
            'LISTEN':0,'ESTABLISHED':0,'TIME_WAIT':0,'CLOSE_WAIT':0,'SYN_RECV':0,
            'LAST_ACK':0,'SYN_SENT':0,'NONE':0,'FIN_WAIT2':0,'FIN_WAIT1':0,
        }#连接状态
        self.PID_PORT_DICT = {}  #进程号 端口 字典
        self.CONN_LIST = [] #连接列表
        self.EXPECT_PORT_PID_DIC = {}  #剔除的端口号

class Grep_Pro_Status(threading.Thread): #状态 4
    def __init__(self):
        threading.Thread.__init__(self)

    def command_getter(self,command):
        com = re.split("\d",command)[0]
        if com in COMMAND_MAP:  #匹配数字并剔除
            pid = eval(re.split("\D",command)[-1])
            info = None
            try:
                flag = com.split()
                if flag[0] =='kill':
                    try:
                        print(COMMAND_MAP[com].format(pid))
                        eval(COMMAND_MAP[com].format(pid))
                        info = "成功"
                    except:
                        info = "失败"
                else:
                    p = psutil.Process(pid)
                    info = eval("p" + COMMAND_MAP[com])
                    if flag[2] == 'time':
                        info = datetime.datetime.fromtimestamp(info).strftime("%Y-%m-%d %H:%M:%S")
            except:
                info = "没有找到该进程"

            return info
        else:
            return "Command error!"

    def runner(self,command):
        return self.command_getter(command)


class Cpu_Status():

    def __init__(self): #协程
        self.ioloop = asyncio.get_event_loop()
        self.task_00 = self.ioloop.create_task(self.cpu_percent_getter())
        self.task_01 = self.ioloop.create_task(self.memory_data_getter())
        self.task_02 = self.ioloop.create_task(self.swap_memory_getter())
        self.tasks = [
            self.task_00,self.task_01,self.task_02
        ]
    async def cpu_percent_getter(self):
        return psutil.cpu_percent(interval=1,percpu=True) # 获取每个CPU的使用率

    async def memory_data_getter(self):
        return psutil.virtual_memory() #获取内存统计数据，单位bytes，

    async def swap_memory_getter(self):
        return psutil.swap_memory() # 获取swap的统计数据

    def runner(self):
        #start = time.time()
        try:
            self.ioloop.run_until_complete(asyncio.wait(self.tasks))

            cpu_status_list = [self.task_00.result(),self.task_01.result(),self.task_02.result()]
        #print('at %1.1f seconds' % (time.time() - start))

            return cpu_status_list
        except:
            self.ioloop.close()
            return []

    # def run(self):
    #     while True:
    #         print(self.cpu_percent_getter())
    #         print(self.memory_data_getter())
    #         print(self.swap_memory_getter())

class Pid_Status_Info():

    def net_conn_info(self):
        net_conn = psutil.net_connections()# 获取网络连接信息  n个元组

        for conn_info in net_conn:
            yield conn_info

    def filter_conn_data(self): #串行事件  无法用协程

        generator = self.net_conn_info()
        data_dict = Data_Dict_Init()
        i = 0
        for item in generator:
            data_dict.CONN_STATUS[item.status] += 1

            if item.laddr.ip in EXPECT_LADDR and item.pid in data_dict.EXPECT_PORT_PID_DIC and item.laddr.port not in \
                    data_dict.EXPECT_PORT_PID_DIC[item.pid]:  # 获取需要剔除的地址的端口  然后针对pid 剔除 无用的端口

                data_dict.EXPECT_PORT_PID_DIC[item.pid].append(item.laddr.port)
                continue
            elif item.laddr.ip in EXPECT_LADDR : #当不满足  上面全部条件 即 可能满足 此 一个条件 故 初始化
                data_dict.EXPECT_PORT_PID_DIC[item.pid] = []
                data_dict.EXPECT_PORT_PID_DIC[item.pid].append(item.laddr.port)
                continue

            # if item.pid in data_dict.EXPECT_PORT_PID_DIC and item.laddr.port in data_dict.EXPECT_PORT_PID_DIC[item.pid]:
            #     continue
            if item.pid in data_dict.PID_PORT_DICT:
                pass
            else:
                data_dict.PID_PORT_DICT[item.pid] = []

            data_dict.PID_PORT_DICT[item.pid].append(item.laddr.port)
            i += 1
        #time.sleep(0.5)  # 程序运行太快会在一次传输多组数据
        return [i, data_dict.CONN_STATUS, self.pid_solver(data_dict.PID_PORT_DICT)]

    def pid_solver(self,dic):
        # PID_PORTS_NUM = sorted(dic.items(),key= lambda item: len(item[1]))  #sorted 为 升序 故 reverse 一下
        PID_PORTS_NUM = sorted(dic.items(), key=lambda item: len(item[1]))
        return PID_PORTS_NUM[::-1]

    def runner(self):
        return self.filter_conn_data()

# if __name__ == "__main__":
#     ss = Pid_Status_Info()
#     ss.runner()

    # ss = Pid_Status_Info()
  #  c = Cpu_Status()
#  #   c.start()
#  #
#     ss = Pid_Status_Info()
#

#     ss.runner()
