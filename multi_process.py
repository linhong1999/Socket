import multiprocessing
import time
def func(msg):
  for i in range(2):
    print(msg)
    time.sleep(1)
if __name__ == "__main__":
  pool = multiprocessing.Pool(processes=4)
  result = []
  for i in range(10):
    msg = "hello %d" %(i)
    pool.apply_async(func, (msg, ))
  pool.close()
  pool.join()
  print("Sub-process(es) done.")
  for res in result:
      print(res.get())
  print("Sub-process(es) done.")