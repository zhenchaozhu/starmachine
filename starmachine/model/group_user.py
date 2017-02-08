# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.utils import get_int_date
from starmachine.lib.redis_cache import CacheManager
from starmachine.rong.rong_client import rong_client
from starmachine.model.consts import GROUP_USER_CACHE_KEY, USER_GROUP_CACHE_KEY, GROUP_USER_COUNT_KEY, \
    GROUP_USER_CREATOR, JOIN_GROUP_LIMIT


class GroupUser(object):

    table = 'rong_group_user'

    def __init__(self, id=None, group_id=None, user_id=None, status=None, join_time=None, last_voice_time=None):
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.status = status
        self.join_time = join_time
        self.last_voice_time = last_voice_time

    @classmethod
    def add_group_user(cls, group_id, group_name, user_id, status):
        cache = CacheManager().cache
        db = DbManager().db
        join_time = datetime.now()
        score = get_int_date(join_time)
        db.execute('begin;')
        try:
            sql = 'insert into {table} (group_id, user_id, status, join_time) values (%s, %s, %s, %s)'.format(table=cls.table)
            db.execute(sql, group_id, user_id, status, join_time)
            rong_client.group_join([user_id], group_id, group_name)
            db.execute('commit;')
        except Exception:
            db.execute('rollback;')
            raise

        cache.zincrby(GROUP_USER_COUNT_KEY, group_id, 1)
        group_user_cache = GROUP_USER_CACHE_KEY % group_id
        user_group_cache = USER_GROUP_CACHE_KEY % user_id
        cache.zadd(group_user_cache, score, user_id)
        cache.zadd(user_group_cache, score, group_id)

    @classmethod
    def get_users_by_group(cls, group_id, start=0, count=10):
        cache = CacheManager().cache
        group_user_cache = GROUP_USER_CACHE_KEY % group_id
        end = start + count - 1
        user_ids = cache.zrange(group_user_cache, start, end)
        return user_ids

    @classmethod
    def get_user_joined_groups(cls, user_id):
        cache = CacheManager().cache
        # end = start + count - 1
        redis_key = USER_GROUP_CACHE_KEY % user_id
        group_ids = cache.zrevrange(redis_key, 0, -1)
        return group_ids

    @classmethod
    def get_user_amount_by_group(cls, group_id):
        cache = CacheManager().cache
        redis_key = GROUP_USER_CACHE_KEY % group_id
        return cache.zcard(redis_key)

    @classmethod
    def get_by_group_and_user(cls, group_id, user_id):
        db = DbManager().db
        sql ='select * from {table} where group_id=%s and user_id=%s'.format(table=cls.table)
        rst = db.get(sql, group_id, user_id)
        return rst and cls(**rst)

    @classmethod
    def remove_and_black_user(cls, group_id, user_id):
        remove_time = datetime.now()
        db = DbManager().db
        db.execute('begin;')
        try:
            sql = 'delete from {table} where group_id=%s and user_id=%s'.format(table=cls.table)
            db.execute(sql, group_id, user_id)
            sql = 'insert into {table} (group_id, user_id, create_time) values (%s, %s, %s)'.format(
                table=GroupBlackUser.table)
            db.execute(sql, group_id, user_id, remove_time)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        cache = CacheManager().cache
        group_user_key = GROUP_USER_CACHE_KEY % group_id
        user_group_key = USER_GROUP_CACHE_KEY % user_id
        cache.zrem(group_user_key, user_id)
        cache.zrem(user_group_key, group_id)
        cache.zincrby(GROUP_USER_COUNT_KEY, group_id, -1)
        rong_client.group_quit([user_id], group_id)

    @classmethod
    def update_voice_time(cls, group_id, user_id):
        voice_time = datetime.now()
        db = DbManager().db
        cache = CacheManager().cache
        sql = 'update {table} set last_voice_time=%s where group_id=%s and user_id=%s'.format(table=cls.table)
        db.execute(sql, voice_time, group_id, user_id)
        redis_key = USER_GROUP_CACHE_KEY % user_id
        score = get_int_date(voice_time)
        cache.zadd(redis_key, score, group_id)

    @classmethod
    def get_pressed_user_by_group(cls, group_id):
        db = DbManager().db
        sql = 'select * from {table} where group_id=%s order by last_voice_time limit 1'
        rst = db.get(sql, group_id)
        obj = cls(**rst)
        last_voice_time = obj.last_voice_time
        if not last_voice_time:
            return obj.user_id
        else:
            now = datetime.now()
            if (now - last_voice_time).seconds > 24 * 60 * 60:
                return obj.user_id

            return None

    @classmethod
    def is_over_join_limit(cls, user_id):
        cache = CacheManager().cache
        cache_key = USER_GROUP_CACHE_KEY % user_id
        return cache.zcard(cache_key) >= JOIN_GROUP_LIMIT

    def delete(self):
        cache = CacheManager().cache
        user_id = self.user_id
        group_id = self.group_id
        db = DbManager().db
        db.execute('begin;')
        try:
            sql = 'delete from {table} where id=%s'.format(table=self.table)
            db.execute(sql, self.id)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        cache.zincrby(GROUP_USER_COUNT_KEY, self.group_id, -1)
        group_user_cache = GROUP_USER_CACHE_KEY % group_id
        user_group_cache = USER_GROUP_CACHE_KEY % user_id
        cache.zrem(group_user_cache, user_id)
        cache.zrem(user_group_cache, group_id)
        rong_client.group_quit([user_id], group_id)

    def has_group_user_handle_access(self, remove_group_user):
        if self.user_id != remove_group_user.user_id:
            if int(self.status) == GROUP_USER_CREATOR:
                return True

        return False


class GroupBlackUser(object):

    table = 'group_black_user'

    def __init__(self, id=None, group_id=None, user_id=None, create_time=None):
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.create_time = create_time

    @classmethod
    def add(cls, group_id, user_id):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (group_id, user_id, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, group_id, user_id, create_time)

    @classmethod
    def is_group_black_user(cls, group_id, user_id):
        db = DbManager().db
        sql = 'select id from {table} where group_id=%s and user_id=%s'.format(table=cls.table)
        try:
            return db.query(sql, group_id, user_id)[0]
        except:
            return None