# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.utils import get_int_date
from starmachine.model.consts import CHECK_STATUS_PENDING, CHECK_STATUS_PASS, CHECK_STATUS_REJECT, USER_DAILY_RECEIVE_LIKE_COUNT
from starmachine.model.user import User

tag_proverbs_liked_key = 'tag:proverbs:%s:liked'
tag_proverbs_liked_rank = 'tag:proverbs:liked:rank'
user_tag_proverbs_24_hours_limit = 'tag:proverb:user:%s:24:limit'
LIMIT_SECONDS = 24 * 60 * 60

class TagProverbs(object):

    table = 'tag_proverbs'

    def __init__(self, id=None, creator_id=None, proverbs=None, status=None, create_time=None, check_time=None, extra=None):
        self.id = id
        self.creator_id = creator_id
        self.proverbs = proverbs
        self.status = status
        self.create_time = create_time
        self.check_time = check_time
        self.extra = extra

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def like_amount(self):
        cache = CacheManager().cache
        redis_key = tag_proverbs_liked_key % self.id
        return cache.zcard(redis_key)

    @classmethod
    def add(cls, creator_id, proverbs, status=CHECK_STATUS_PENDING):
        create_time = datetime.now()
        db = DbManager().db
        cache = CacheManager().cache
        sql = 'insert into {table} (creator_id, proverbs, status, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        proverbs_id = db.execute(sql, creator_id, proverbs, status, create_time)
        if proverbs_id:
            user_tag_proverbs_limit_key = user_tag_proverbs_24_hours_limit % creator_id
            cache.set(user_tag_proverbs_limit_key, 'true')
            cache.expire(user_tag_proverbs_limit_key, LIMIT_SECONDS)
            return cls(proverbs_id, creator_id, proverbs, status, create_time, None, None)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def get_random_list(cls, count=6):
        db = DbManager().db
        sql = 'select * from {table} as t1 join(select round(rand() * ((select max(id) from {table}) - ' \
              '(select min(id) from {table})) + (select min(id) from {table})) as id) as t2 where ' \
              't1.id >= t2.id and status="{status}" ORDER BY t1.id LIMIT 1'.format(table=cls.table, status=CHECK_STATUS_PASS)
        rst = db.get(sql)
        if rst:
            rst = set()
            while len(rst) < count:
                id = int(db.get(sql).get('id'))
                rst.add(id)
            tlist = []
            for r in rst:
                tag = TagProverbs.get(r)
                tlist.append(tag)
            return tlist

        return []

    @classmethod
    def get_pass_proverb(cls):
        db = DbManager().db
        sql = 'select id from {table} where status=%s'.format(table=cls.table)
        rst = db.query(sql, CHECK_STATUS_PASS)
        return rst and [cls.get(rst[0].get('id'))]

    @classmethod
    def has_time_limit(cls, user_id):
        cache = CacheManager().cache
        user_tag_proverbs_limit_key = user_tag_proverbs_24_hours_limit % user_id
        return cache.exists(user_tag_proverbs_limit_key)

    def pass_proverbs(self, extra):
        db = DbManager().db
        check_time = datetime.now()
        sql = 'update {table} set status=%s, check_time=%s, extra=%s where id=%s'.format(table=self.table)
        db.execute(sql, CHECK_STATUS_PASS, extra, check_time, self.id)

    def reject(self, extra):
        db = DbManager().db
        check_time = datetime.now()
        sql = 'update {table} set status=%s, check_time=%s, extra=%s, where id=%s'.format(table=self.table)
        db.execute(sql, CHECK_STATUS_REJECT, extra, check_time, self.id)

    def jsonify(self, user=None):
        result =  {
            'id': self.id,
            'creator': {
                'id': self.creator.id,
                'name': self.creator.user_name,
                'avatar': self.creator.avatar_url,
            },
            'proverbs': self.proverbs,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'check_time': self.check_time.strftime('%Y-%m-%d %H:%M:%S') if self.check_time else None,
            'extra': self.extra,
            'like_amount': self.like_amount,
        }
        if user:
            has_liked = TagProverbsLiked.has_liked(user.id, self.id)
            result.update({
                'has_liked': bool(has_liked),
            })

        return result


class TagProverbsLiked(object):

    table = 'tag_proverbs_liked'

    def __init__(self, id=None, user_id=None, proverbs_id=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.proverbs_id = proverbs_id
        self.create_time = create_time

    # 添加赞，如果已经添加了赞则取消赞，返回点赞总数
    @classmethod
    def add(cls, user_id, proverbs_id, receiver_id):
        cache = CacheManager().cache
        create_time = datetime.now()
        date = create_time.date()
        score = get_int_date(create_time)
        key = tag_proverbs_liked_key % proverbs_id
        user_daily_like_count_redis_key = USER_DAILY_RECEIVE_LIKE_COUNT % (receiver_id, date)
        if cache.zscore(key, user_id):
            cache.zrem(key, user_id)
            cache.zincrby(tag_proverbs_liked_rank, proverbs_id, -1)
            cache.incr(user_daily_like_count_redis_key, -1)
            cls.delete_proverbs_like(user_id, proverbs_id)
            return cache.zcard(key)

        cache.zadd(key, score, user_id)
        cache.zincrby(tag_proverbs_liked_rank, proverbs_id, 1)
        cache.incr(user_daily_like_count_redis_key, 1)
        cls.add_proverbs_like(user_id, proverbs_id, create_time)
        return cache.zcard(key)

    @classmethod
    def add_proverbs_like(cls, user_id, proverbs_id, create_time):
        db = DbManager().db
        sql = 'insert into {table} (user_id, proverbs_id, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, proverbs_id, create_time)

    @classmethod
    def delete_proverbs_like(cls, user_id, proverbs_id):
        db = DbManager().db
        sql = 'delete from {table} where user_id=%s and proverbs_id=%s'.format(table=cls.table)
        db.execute(sql, user_id, proverbs_id)

    @classmethod
    def has_liked(cls, user_id, proverbs_id):
        cache = CacheManager().cache
        key = tag_proverbs_liked_key % proverbs_id
        return cache.zscore(key, user_id)
