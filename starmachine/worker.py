# coding: utf-8

import os
import redis
from rq import Worker, Queue, Connection

profile = os.environ.get('profile', 'local')

listen = ['high', 'default', 'low']

redis_url = 'redis://localhost:6379'
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()