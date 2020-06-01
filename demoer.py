# a = [1,2,3,4]
# count = 0
# time = 0
# for i in range(len(a)):
#     m= a.pop(i)
#     for j in range(len(a)):
#         n = a.pop(j)
#         for k in range(len(a)):
#             print(str(m) + str(n) + str(a[k]),end= ' ')
#             count+=1
#
#         print(a)
#         a.insert(j,n)
#         print(a)
#     print()
#     a.insert(i,m)
#     print("aaaa")
#     print(a)
#

# import asyncio
# import time
#
# start = time.time()
#
#
# def tic():
#     return 'at %1.1f seconds' % (time.time() - start)
#
#
# async def gr1():
#     # Busy waits for a second, but we don't want to stick around...
#     print('gr1 started work: {}'.format(tic()))
#     # 暂停两秒，但不阻塞时间循环，下同
#     await asyncio.sleep(1)
#     print('gr1 ended work: {}'.format(tic()))
#     return "1111111111111"
#
#
# async def gr2():
#     # Busy waits for a second, but we don't want to stick around...
#     print('gr2 started work: {}'.format(tic()))
#     await asyncio.sleep(2)
#     print('gr2 Ended work: {}'.format(tic()))
#     return "2222222222222"
#
#
# async def gr3():
#     print("Let's do some stuff while the coroutines are blocked, {}".format(tic()))
#     await asyncio.sleep(3)
#     print("Done!")
#     return "33333333333333"
#
# # 事件循环
# ioloop = asyncio.get_event_loop()
#
# # tasks中也可以使用asyncio.ensure_future(gr1())..
# task_00 = ioloop.create_task(gr1())
# task_01 = ioloop.create_task(gr2())
# task_02 = ioloop.create_task(gr3())
# tasks = [
#     task_00,task_01,task_02
# ]
#
# ioloop.run_until_complete(asyncio.wait(tasks))
#
# print(task_00.result())
# print(task_01.result())
# print(task_02.result())
#
# ioloop.close()


# import threading
# import time
# import logging
#
# logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s', )
#


# def worker_00(event):
#     logging.debug('Waiting for redis ready...')
#     event.wait()
#     logging.debug('redis ready, and connect to redis server and do some work [%s]', time.ctime())
#
# def worker_01(event):
#     logging.debug('Waiting for redis ready...')
#     event.wait()
#     logging.debug('redis ready, and connect to redis server and do some work [%s]', time.ctime())
#
#
#
# def main():
#     readis_ready = threading.Event()
#     t1 = threading.Thread(target=worker_00, args=(readis_ready,), name='t1')
#     t1.start()
#
#     t2 = threading.Thread(target=worker_01, args=(readis_ready,), name='t2')
#     t2.start()
#
#     logging.debug('first of all, check redis server, make sure it is OK, and then trigger the redis ready event')
#     time.sleep(3)  # simulate the check progress
#     readis_ready.set()
#
#
# if __name__ == "__main__":
#     main()

from matplotlib import pyplot as plt


# 元胞自动机、流言模型


def count_rumour(matrix, rumour):  # 二维矩阵,计算流言的数目
    sum_rumour = 0
    for sublist in matrix:
        sum_rumour += sublist.count([0, rumour]) + sublist.count([rumour, rumour])
    return sum_rumour


def spread(size, rumour, start_x, start_y):
    # 初始化
    rumour_matrix = [[[0, 0] for i in range(size)] for j in range(size)]
    rumour_spread = []
    rumour_matrix[start_x][start_y] = [1, 1]
    rumour_spread.append(count_rumour(rumour_matrix, rumour))
    # 个体更新
    while count_rumour(rumour_matrix, rumour) < size * size:
        for i in range(size):
            for j in range(size):
                # 制定流言传播规则1、准备传播流言的传播给邻居（上下左右）2、上次听到流言的，变为准备传播流言
                if rumour_matrix[i][j][0] == rumour:
                    if i - 1 >= 0:
                        rumour_matrix[i - 1][j] = [rumour, rumour]  # 已经遍历了
                    if i + 1 < size:
                        rumour_matrix[i + 1][j][1] = rumour
                    if j - 1 >= 0:
                        rumour_matrix[i][j - 1] = [rumour, rumour]  # 已经遍历了
                    if j + 1 < size:
                        rumour_matrix[i][j + 1][1] = rumour
                elif rumour_matrix[i][j][1] == rumour:
                    rumour_matrix[i][j][0] = rumour
        rumour_spread.append(count_rumour(rumour_matrix, rumour))
    print(rumour_spread[:10])  # 打印前十个时间步流言传播的速度
    plt.plot(rumour_spread)


# 设置参数
size = 200
rumour = 1
# 最里面的列表中第2个元素为rumour说明更新刚听到流言，第1个元素为rumour说明准备传播流言
center_x, center_y = int(size / 2), int(size / 2)
spread(size, rumour, center_x, center_y)
spread(size, rumour, 0, 0)
plt.show()
