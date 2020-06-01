import socket
import threading
import os,asyncio
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

METHOD_MAP = {
    '1':"get_cpu_core_num",'2':"cup_status_runner",'3':"filter_conn_data",'4':"process_status",
}
COMMAND_MAP = {
    "get name -p ":".name()","get status -p ":".status()",
    "get memory precent -p ": ".memory_percent()","get threads -p ": ".num_threads()",
    "get create time -p ": ".create_time()","kill -p -l":"os.kill({},signal.SIGKILL)",
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
        self.CONN_LIST = []
        self.EXPECT_PORT_PID_DIC = {}  #剔除的端口号

class Grep_Pro_Status(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def command_getter(self,command):
        com = re.split("\d",command)[0]
        print(com)
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
    # def cpu_percent_getter(self):
    #     return psutil.cpu_percent(interval=1,percpu=True) # 获取每个CPU的使用率
    #
    # def memory_data_getter(self):
    #     return psutil.virtual_memory() #获取内存统计数据，单位bytes，
    #
    # def swap_memory_getter(self):
    #     return psutil.swap_memory() # 获取swap的统计数据
    #
    # def runner(self):
    #     start = time.time()
    #     cpu_status_list = [self.cpu_percent_getter(),self.memory_data_getter(),self.swap_memory_getter()]
    #     print('at %1.1f seconds' % (time.time() - start))
    #     return cpu_status_list
    def __init__(self):
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
    #
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
            data_dict.CONN_LIST.append(item)  # 边 迭代 边去重
            if item.laddr.ip in EXPECT_LADDR and item.pid in data_dict.EXPECT_PORT_PID_DIC and item.laddr.port not in \
                    data_dict.EXPECT_PORT_PID_DIC[item.pid]:  # 获取需要剔除的地址的端口  然后针对pid 剔除 无用的端口
                print(item.laddr.ip)
                print(item.pid)
                data_dict.EXPECT_PORT_PID_DIC[item.pid].append(item.laddr.port)
                data_dict.CONN_LIST.pop()
                continue
            elif item.laddr.ip in EXPECT_LADDR:
                print("ssssssssssssss",item.laddr.ip)
                print("xxxxxxxxxxxxxxxx",item.pid)
                data_dict.EXPECT_PORT_PID_DIC[item.pid] = []
                data_dict.EXPECT_PORT_PID_DIC[item.pid].append(item.laddr.port)
                data_dict.CONN_LIST.pop()
                continue
            if item.pid in data_dict.EXPECT_PORT_PID_DIC and item.laddr.port in data_dict.EXPECT_PORT_PID_DIC[item.pid]:
                data_dict.CONN_LIST.pop()
                continue
            if item.pid in PID_PORT_DICT:
                pass
            else:
                data_dict.PID_PORT_DICT[item.pid] = []

            data_dict.PID_PORT_DICT[item.pid].append(item.laddr.port)
            i += 1
        print("进程数量",i)
        print("------------",data_dict.CONN_STATUS)
        print("============",data_dict.PID_PORT_DICT)
       # time.sleep(0.5)  # 程序运行太快会在一次传输多组数据
        return [i, data_dict.CONN_STATUS, self.pid_solver(data_dict.PID_PORT_DICT)]

    def pid_solver(self,dic):
        # PID_PORTS_NUM = sorted(dic.items(),key= lambda item: len(item[1]))  #sorted 为 升序 故 reverse 一下
        PID_PORTS_NUM = sorted(sorted(dic.items(), key=lambda item: len(item[1])), reverse=True)
        print(PID_PORTS_NUM)
        return PID_PORTS_NUM

    def runner(self):
        return self.filter_conn_data()



class Solver():
    def __init__(self, ip,msg):
        self.ip = ip
        self.msg = msg

    def get_cpu_core_num(self): #  只调用一次   初始化的时候
        cpu_num = psutil.cpu_count() # 逻辑CPU核数

        return psutil.cpu_count()

    def cup_status(self):   #实时数据   三个都是实时的

        while 1:

            cpu_percent = psutil.cpu_percent(interval=1,percpu=True) # 获取每个CPU的使用率

            memory_data = psutil.virtual_memory() #获取内存统计数据，单位bytes，
            swap_memory = psutil.swap_memory() # 获取swap的统计数据   ?????

            SVMEN = {
                'total': memory_data.total, 'available': memory_data.available,\
                'percent': memory_data.percent, 'used': memory_data.used, 'free': memory_data.free
            }
            SSWAP = {
                'total': swap_memory.total, 'used': swap_memory.used, 'free': swap_memory.free,\
                'percent': swap_memory.percent, 'sin': swap_memory.sin, 'sout': swap_memory.sout
            }

            CPU_STATUS = [cpu_percent,SSWAP,SVMEN]

        #    sys.stdout.write("\r{}\n{}\n{}".format(cpu_percent,SSWAP,SVMEN))

            print("\r",cpu_percent)
            print("\r",SSWAP)
            print("\r",SVMEN)
            # print("\r".format(cpu_percent,SSWAP,SVMEN),end=' ')
            time.sleep(1)

    def cpu_status_lisner(self):
        while 1:
            print("\r",CPU_STATUS,end=" ")
            time.sleep(1)
        # return CPU_STATUS

    def cup_status_runner(self):
        cpu_status_getter = threading.Thread(target=self.cup_status)
     #   open_lisner = threading.Thread(target=self.cpu_status_lisner)

        cpu_status_getter.start()
     #   open_lisner.start()

    def net_conn_info(self):
        net_conn = psutil.net_connections()# 获取网络连接信息  n个元组
    #    top = [psutil.cpu_percent(interval=i, percpu=True) for i in range(4)]  # 设置每秒刷新时间间隔，统计十次的结果  //可绘图

      #  print(cpu_num)
      #  print(cpu_percent)
      #   i = 0
        for conn_info in net_conn:
            yield conn_info
        #     i+=1
        #     print(conn_info)# 有个fd 参数 为文件描述符 一直都是=-1 应该是没有权限获取
        # print(i)
      #  print(type(memory_data))   #<class 'psutil._pswindows.svmem'>
      #  print(type(swap_memory))   #<class 'psutil._common.sswap'>
      #  print(type(net_conn[0]))   #<class 'psutil._common.sconn'>

    #    print(top)

    def process_status(self):
        pid = eval(input("请输入进程PID: "))
        pid_info = psutil.Process(pid)


        print("进程PID {},进程名{},进程CPU使用率{},进程使用的内存{},进程的线程数量{}".format(pid,pid_info.name(),\
                                                          pid_info.cpu_percent(interval=1),pid_info.memory_percent(),pid_info.num_threads()))


    def _getter(self,select_num):
        __getter = select_num
        return eval("self.{}()".format(METHOD_MAP[__getter]))

    def filter_conn_data(self):
        generator = self.net_conn_info()

        i = 0
        items = generator.__next__()
        try:
            while items:
                CONN_STATUS[items.status] += 1
                CONN_LIST.append(items)  # 边 迭代 边去重
                if items.laddr.ip in EXPECT_LADDR and items.pid in EXPECT_PORT_PID_DIC and items.laddr.port not in \
                        EXPECT_PORT_PID_DIC[items.pid]:  # 获取需要剔除的地址的端口  然后针对pid 剔除 无用的端口
                    EXPECT_PORT_PID_DIC[items.pid].append(items.laddr.port)
                    CONN_LIST.pop()
                    items = generator.__next__()
                    continue
                elif items.laddr.ip in EXPECT_LADDR:
                    EXPECT_PORT_PID_DIC[items.pid] = []
                    EXPECT_PORT_PID_DIC[items.pid].append(items.laddr.port)
                    CONN_LIST.pop()
                    items = generator.__next__()
                    continue
                if items.pid in EXPECT_PORT_PID_DIC and items.laddr.port in EXPECT_PORT_PID_DIC[items.pid]:
                    CONN_LIST.pop()
                    items = generator.__next__()
                    continue
                if items.pid in PID_PORT_DICT:
                    pass
                else:
                    PID_PORT_DICT[items.pid] = []

                PID_PORT_DICT[items.pid].append(items.laddr.port)
                i += 1
                #   time.sleep(0.5)
                items = generator.__next__()
        except Exception:
            print(i)
            print(CONN_STATUS)
            print(PID_PORT_DICT)
            print()
            # PID_PORT_DICT = sorted(PID_PORT_DICT.items(), key=lambda item: item[0])

            return [i,CONN_STATUS,self.pid_solver()]

        return [i,CONN_STATUS,PID_PORT_DICT]

    def pid_solver(self):

        PID_PORTS_NUM = sorted(PID_PORT_DICT.items(),key= lambda item: len(item[1]))

        # PID_PORTS_NUM = sorted(sorted(PID_PORT_DICT.items(),key= lambda item: len(item[1])),reverse=True)
        print("******************",PID_PORTS_NUM[::-1])

        return PID_PORTS_NUM
if __name__ == "__main__":
    ss = Pid_Status_Info()
    ss.runner()
    s = Solver("127.0.0.1", "")
    generator = s._getter("3")
    # ss = Pid_Status_Info()
#   #  c = Cpu_Status()
#  #   c.start()
#  #
#     ss = Pid_Status_Info()
#

#     ss.runner()
