'''
Server Listener
Author Hong Lin
Created on 1 st，November 2019
'''
lin_starter.py
#此为连接服务端脚本
'''
param :flag,server_ip
通过cmd命令行获取参数
flag: 2 获取CPU状态指令 3 获取进程状态指令 4 启动命令行模式
server_ip: 不同的ip对应着不同的服务端
状态2，3 属于同一进程，4为一独立进程，一般服务端连接多个，而4只需开一个
进入 4 状态后 选择服务器后建立连接 可输入不同的命令从服务端获取相应的内容
当命令行输入exit后断开本次连接，可重新选择服务器
'''
solver.py
#此为数据处理脚本
'''
协程获取cpu状态，串行处理进程信息
由于cpu各个状态可独立获取，且耗费一定的时间，故采用协程
由于进程状态需要对占用端口数进行优先级排列，且需先统计出进程状态列表，
且对于一些无用的端口进行过滤，故采用迭代器
'''
reciver_01.py
#此为服务端监听脚本
sudo python3 reciver_01.py 即可开始监听，分三个线程
分别处理CPU状态，进程状态，以及监听客户端命令行并返回数据
为了减轻客户端压力，故数据全在服务器端处理 solver.py
处理后返回给客户端