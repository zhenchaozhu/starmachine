# coding: utf-8

from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from starmachine import settings
redis_host = settings.REDIS_HOST
redis_port = settings.REDIS_PORT

jobstores = {
    # 'redis': RedisJobStore(    ('123.57.46.53', 6379)),
    'default': RedisJobStore(host=redis_host, port=redis_port)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

tornado_scheduler = TornadoScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
tornado_scheduler.start()