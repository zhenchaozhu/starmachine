# coding: utf-8

import redis
from starmachine import settings


_redis_servers = {}
for key, value in settings.CACHE_SERVERS.items():
    _redis_servers[key] = redis.StrictRedis(*value, socket_timeout=1)

class CacheManager(object):

    def __init__(self, server='default'):
        self.cache = _redis_servers[server]


