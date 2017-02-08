# coding: utf-8

import time
from datetime import datetime
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.query import DbManager
from starmachine.model.user import User
from starmachine.model.consts import CONTENT_LIKED_CACHE_KEY, POSTS_LIKED_RANK_KEY, VOTE_LIKED_RANK_KEY, WELFARE_LIKED_RANK_KEY, POSTS_TYPE, \
    VOTE_TYPE, WELFARE_TYPE, CONTENT_LIKED_RANK_KEY, USER_LIKED_CONTENT_KEY, USER_DAILY_RECEIVE_LIKE_COUNT
from starmachine.lib.utils import get_int_date

CONTENT_RANK_KEY_MAP = {
    POSTS_TYPE: POSTS_LIKED_RANK_KEY,
    VOTE_TYPE: VOTE_LIKED_RANK_KEY,
    WELFARE_TYPE: WELFARE_LIKED_RANK_KEY,
}

class ContentLiked(object):

    table = 'content_liked'

    def __init__(self, id=None, content_id=None, content_type=None, user_id=None, create_time=None):
        self.id = id
        self.content_id = content_id
        self.content_type = content_type
        self.user_id = user_id
        self.create_time = create_time

    def __repr__(self):
        return '<ContentLiked:id=%s>' % (self.id)

    # 添加赞，如果已经添加了赞则取消赞，返回点赞总数
    @classmethod
    def add(cls, content_id, content_type, user_id, receiver_id):
        from starmachine.jobs.user import add_content_like, delete_conetnt_like
        cache = CacheManager().cache
        create_time = datetime.now()
        date = create_time.date()
        score = get_int_date(create_time)
        key = CONTENT_LIKED_CACHE_KEY % content_id
        # CONTENT_TYPE_RANK_KEY = CONTENT_RANK_KEY_MAP.get(content_type)
        user_daily_redis_key = USER_DAILY_RECEIVE_LIKE_COUNT % (receiver_id, date)
        if cache.zscore(key, user_id):
            cache.zrem(key, user_id)
            cache.zincrby(CONTENT_LIKED_RANK_KEY, content_id, -1)
            # cache.zincrby(CONTENT_TYPE_RANK_KEY, content_id, -1)
            cache.incr(user_daily_redis_key, -1)
            delete_conetnt_like.delay(content_id, content_type, user_id)
            cache.zrem(USER_LIKED_CONTENT_KEY % user_id, content_id)
            return cache.zcard(key)

        cache.zadd(key, score, user_id)
        cache.zadd(USER_LIKED_CONTENT_KEY % user_id, score, content_id)
        cache.zincrby(CONTENT_LIKED_RANK_KEY, content_id, 1)
        # cache.zincrby(CONTENT_TYPE_RANK_KEY, content_id, 1)
        cache.incr(user_daily_redis_key, 1)
        add_content_like.delay(content_id, content_type, user_id)
        return cache.zcard(key)

    @classmethod
    def delete_from_mysql(cls, content_id, content_type, user_id):
        db = DbManager().db
        sql = 'delete from {table} where content_id=%s and content_type=%s and user_id=%s'.format(table=cls.table)
        db.execute(sql, content_id, content_type, user_id)

    @classmethod
    def add_mysql(cls, content_id, content_type, user_id):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (content_id, content_type, user_id, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, content_id, content_type, user_id, create_time)

    def get_liked_people(self, content_id, start=0, count=10):
        cache = CacheManager().cache
        key = CONTENT_LIKED_CACHE_KEY % content_id
        end = start + count - 1
        user_ids = cache.zrevrange(key, start, end)
        return [User.get(user_id) for user_id in user_ids]

    @classmethod
    def has_liked(cls, content_id, user_id):
        cache = CacheManager().cache
        key = CONTENT_LIKED_CACHE_KEY % content_id
        return cache.zscore(key, user_id)