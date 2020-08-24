import requests
import datetime
import time
from multiprocessing.pool import ThreadPool


def update_stats(start_time):
    global total_time
    global count
    end_time = datetime.datetime.now()
    print(f'Download Time: {end_time - start_time}')
    total_time += (end_time - start_time).total_seconds()
    print(f'Average Download Time: {total_time / (count)}')
    count += 1


def get_url():
    start_time = datetime.datetime.now()
    response = requests.get(r'http://cachefly.cachefly.net/100mb.test')
    return start_time

def loop_get_url():
    sub_pool = ThreadPool(1)
    loop_count = 1
    while loop_count <= 180:
        sub_pool.apply_async(get_url, callback=update_stats)
        loop_count += 1
        time.sleep(0)
    sub_pool.close()
    sub_pool.join()


thread_count = 5
pool = ThreadPool(thread_count)
count = 1
total_time = 0

for i in range(thread_count):
    pool.apply_async(loop_get_url)
    time.sleep(4)

pool.close()
pool.join()

print(f'count: {count}')
