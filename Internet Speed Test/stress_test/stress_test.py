import requests
import datetime
import time
from multiprocessing.pool import ThreadPool

thread_count = 1
pool = ThreadPool(thread_count)

def get_url(url=r'http://cachefly.cachefly.net/100mb.test'):
    total_time = 0
    loop_count = 1
    while loop_count <= 180:
        start_time = datetime.datetime.now()
        response = requests.get(url)
        end_time = datetime.datetime.now()
        print(f'Download Time: {end_time - start_time}')
        total_time += (end_time - start_time).total_seconds()
        print(f'Average Download Time: {total_time / (loop_count * thread_count)}')
        loop_count += 1
        time.sleep(60)

for i in range(thread_count):
    pool.apply_async(get_url)

pool.close()
pool.join()