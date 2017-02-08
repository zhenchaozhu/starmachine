# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import DEVICE_OS
from starmachine.lib.utils import redis_cache_obj
from starmachine.lib.redis_cache import CacheManager

USER_DEVICE_CACHE_KEY = 'user:%s:device'

class Device(object):

    table = 'device'

    def __init__(self, id=None, user_id=None, device_token=None, os=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.device_token = device_token
        self.os = os
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Device:id=%s>' % self.id

    @property
    def os_str(self):
        return DEVICE_OS.get(int(self.os)) or 'Other OS'

    @classmethod
    def add(cls, user_id, device_token, os):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, device_token, os, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        device_id = db.execute(sql, user_id, device_token, os, create_time)
        return device_id and cls.get(device_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        device_info = db.get(sql, id)
        return device_info and cls(**device_info)

    @classmethod
    @redis_cache_obj(USER_DEVICE_CACHE_KEY)
    def get_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        device_info = db.get(sql, user_id)
        return device_info and cls(**device_info)

    def delete(self):
        db = DbManager().db
        sql = 'delete from {table} where user_id=%s'.format(table=self.table)
        db.execute(sql, self.user_id)
        self.flush_device_info()

    def update_device_token(self, device_token, os):
        db = DbManager().db
        update_time = datetime.now()
        sql = 'update {table} set device_token=%s, os=%s, update_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, device_token, os, update_time, self.id)
        self.flush_device_info()

    def flush_device_info(self):
        cache = CacheManager().cache
        key = USER_DEVICE_CACHE_KEY % self.user_id
        cache.delete(key)

    def jsonify(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'os': self.os_str,
            'device_token': self.device_token,
        }