# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.utils import get_int_date
from starmachine.model.consts import FOLLOW_SINGLE_TYPE, FOLLOW_BOTH_TYPE, USER_FOLLOW_KEY, USER_FANS_KEY
from starmachine.model.user import User


class UserFollows(object):

    table = 'user_follows'

    def __init__(self, id=None, user_id=None, follow_id=None, follow_type=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.follow_id = follow_id
        self.follow_type = follow_type
        self.create_time = create_time

    @classmethod
    def follow(cls, user_id, follow_id, follow_type):
        db = DbManager().db
        cache = CacheManager().cache
        create_time = datetime.now()
        score = get_int_date(create_time)
        follow_type = int(follow_type)
        user_follow_key = USER_FOLLOW_KEY % user_id
        user_fans_key = USER_FANS_KEY % follow_id
        cache.zadd(user_follow_key, score, follow_id)
        cache.zadd(user_fans_key, score, user_id)
        db.execute('begin;')
        try:
            sql = 'insert into {table} (user_id, follow_id, follow_type, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
            db.execute(sql, user_id, follow_id, follow_type, create_time)
            sql = 'insert into {table} (follow_id, user_id, create_time) values (%s, %s, %s)'.format(table=UserFans.table)
            db.execute(sql, follow_id, user_id, create_time)
            if follow_type == FOLLOW_BOTH_TYPE:
                sql = 'update {table} set follow_type=%s where user_id=%s and follow_id=%s'.format(table=cls.table)
                db.execute(sql, FOLLOW_BOTH_TYPE, follow_id, user_id)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

    @classmethod
    def unfollow(cls, user_id, follow_id):
        cache = CacheManager().cache
        db = DbManager().db
        user_follow_key = USER_FOLLOW_KEY % user_id
        user_fans_key = USER_FANS_KEY % follow_id
        cache.zrem(user_follow_key, follow_id)
        cache.zrem(user_fans_key, user_id)
        db.execute('begin;')
        try:
            sql = 'select follow_type from {table} where user_id=%s and follow_id=%s'.format(table=cls.table)
            follow_type = int(db.get(sql, user_id, follow_id).get('follow_type'))
            sql = 'delete from {table} where user_id=%s and follow_id=%s'.format(table=cls.table)
            db.execute(sql, user_id, follow_id)
            sql = 'delete from {table} where user_id=%s and fans_id=%s'.format(table=UserFans.table)
            db.execute(sql, follow_id, user_id)
            if follow_type == FOLLOW_BOTH_TYPE:
                sql = 'update {table} set type=%s where user_id=%s and follow_id=%s'.format(table=cls.table)
                db.execute(sql, FOLLOW_SINGLE_TYPE, follow_id, user_id)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

    @classmethod
    def get_follows_by_user(cls, user_id, start=0, count=10):
        cache = CacheManager().cache
        end = start + count - 1
        user_follow_key = USER_FOLLOW_KEY % user_id
        rst = cache.zrevrange(user_follow_key, start, end, True)
        if rst:
            return [{'user_id': d[0], 'follow_time': d[1]} for d in rst]
        else:
            return []

    @classmethod
    def has_followed(cls, user_id, follow_id):
        cache = CacheManager().cache
        cache_key = USER_FOLLOW_KEY % user_id
        if cache.exists(cache_key):
            return cache.zscore(cache_key, follow_id)
        else:
            db = DbManager().db
            sql = 'select id from {table} where user_id=%s and follow_id=%s'.format(table=cls.table)
            try:
                return db.query(sql, user_id, follow_id)[0]
            except:
                return None

    @classmethod
    def follow_each_other(cls, user_id, follow_id):
        db = DbManager().db
        sql = 'select follow_type from {table} where user_id=%s and follow_id=%s'
        rst = db.get(sql, user_id, follow_id)
        if rst:
            return rst.get('follow_type') == FOLLOW_BOTH_TYPE

        return False


class UserFans(object):

    table = 'user_fans'

    def __init__(self, id=None, user_id=None, fans_id=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.fans_id = fans_id
        self.create_time = create_time

    @classmethod
    def get_fans_by_user(cls, user_id, start=0, count=10):
        cache = CacheManager().cache
        end = start + count - 1
        user_fans_key = USER_FANS_KEY % user_id
        rst = cache.zrevrange(user_fans_key, start, end, True)
        if rst:
            return [{'user_id': d[0], 'followed_time': d[1]} for d in rst]
        else:
            return []

    @classmethod
    def is_fans(cls, user_id, fans_id):
        cache = CacheManager().cache
        user_fans_key = USER_FANS_KEY % user_id
        return cache.zscore(user_fans_key, fans_id)
