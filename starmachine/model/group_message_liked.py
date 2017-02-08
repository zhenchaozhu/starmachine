# coding: utf-8

import json
from datetime import datetime, timedelta
from starmachine.lib.query import DbManager
from starmachine.lib.utils import get_int_date
from starmachine.lib.redis_cache import CacheManager

GROUP_MESSAGE_LIKED_KEY = 'group:%s:message:%s:liked'
GROUP_MESSAGE_LIKED_LIST = 'group:%s:message:liked'


class GroupMessage(object):

    table = 'group_message'

    def __init__(self, id=None, creator_id=None, group_id=None, object_name=None, channel_type=None, content=None,
        create_time=None, liked_amount=None):
        self.id = id
        self.creator_id = creator_id
        self.group_id = group_id
        self.object_name = object_name
        self.channel_type = channel_type
        self.content = content
        self.create_time = create_time
        self.liked_amount = liked_amount

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, id, creator_id, group_id, object_name, channel_type, content, create_time):
        db = DbManager().db
        sql = 'insert into {table} (id, creator_id, group_id, object_name, channel_type, content, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, id, creator_id, group_id, object_name, channel_type, content, create_time)

    @classmethod
    def update_amount(cls, message_id, liked_amount):
        db = DbManager().db
        sql = 'update {table} set liked_amount=%s where id=%s'.format(table=cls.table)
        db.execute(sql, liked_amount, message_id)

    @classmethod
    def get_hot_messages(cls, group_id, count):
        db = DbManager().db
        now = datetime.now()
        limit_time = now - timedelta(days=1)
        sql = 'select * from {table} where group_id=%s and create_time>%s and liked_amount>%s order by liked_amount desc limit ' \
        '0, %s'.format(table=cls.table)
        rst = db.query(sql, group_id, limit_time, 0, count)
        return rst and [cls(**d) for d in rst]

    @classmethod
    def get_messages_by_time(cls, time):
        db = DbManager().db
        sql = 'select * from {table} where create_time<%s'.format(table=cls.table)
        rst = db.query(sql, time)
        return rst and [cls(**d) for d in rst]

    def jsonify(self, user=None):
        data = {
            'id': self.id,
            'creator_id': self.creator_id,
            'group_id': self.group_id,
            'object_name': self.object_name,
            'channel_type': self.channel_type,
            'content': self.content,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'liked_amount': int(self.liked_amount),
        }
        if user:
            data.update({
                'has_liked': bool(GroupMessageLiked.has_liked(user.id, self.group_id, self.id))
            })

        return data


class GroupMessageLiked(object):

    table = 'group_message_liked'

    def __init__(self, id=None, user_id=None, group_id=None, message_id=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.group_id = group_id
        self.message_id = message_id
        self.create_time = create_time

    @classmethod
    def get_by_group_and_message(cls, group_id, message_id):
        db = DbManager().db
        sql = 'select * from {table} where group_id=%s and message_id=%s limit 1'.format(table=cls.table)
        rst = db.query(sql, group_id, message_id)
        return rst and cls(**rst[0])

    @classmethod
    def add(cls, user_id, group_id, message_id):
        db = DbManager().db
        cache = CacheManager().cache
        create_time = datetime.now()
        score = get_int_date(create_time)
        redis_key = GROUP_MESSAGE_LIKED_KEY % (group_id, message_id)
        group_message_list_key = GROUP_MESSAGE_LIKED_LIST % group_id
        if cache.zscore(redis_key, user_id):
            sql = 'delete from {table} where user_id=%s and message_id=%s and group_id=%s'.format(table=cls.table)
            db.execute(sql, user_id, message_id, group_id)
            cache.zrem(redis_key, user_id)
            cache.zincrby(group_message_list_key, message_id, -1)
            return cache.zcard(redis_key)

        sql = 'insert into {table} (user_id, group_id, message_id, create_time) values' \
            ' (%s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, group_id, message_id, create_time)
        cache.zadd(redis_key, score, user_id)
        cache.zincrby(group_message_list_key, message_id, 1)
        return cache.zcard(redis_key)

    @classmethod
    def has_liked(cls, user_id, group_id, message_id):
        cache = CacheManager().cache
        redis_key = GROUP_MESSAGE_LIKED_KEY % (group_id, message_id)
        return cache.zscore(redis_key, user_id)

    @classmethod
    def get_liked_message_amount_by_group(cls, group_id):
        cache = CacheManager().cache
        group_message_list_key = GROUP_MESSAGE_LIKED_LIST % group_id
        rst = cache.zrevrange(group_message_list_key, 0, -1, True)
        data = []
        for d in rst:
            message_id = d[0]
            amount = d[1]
            message = GroupMessage.get(message_id)
            if message:
                message_creator_id = message.creator_id
                data.append({
                    'message_id': message_id,
                    'amount': amount,
                    'creator_id': message_creator_id,
                })

        return data

    @classmethod
    def get_liked_message_by_user_and_group(cls, user_id, group_id):
        db = DbManager().db
        sql = 'select message_id from {table} where user_id=%s and group_id=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, group_id)
        return rst and [d.get('message_id') for d in rst]

    @classmethod
    def get_liked_message_by_group(cls, group_id, start=0, count=10):
        cache = CacheManager().cache
        group_message_list_key = GROUP_MESSAGE_LIKED_LIST % group_id
        end = start + count - 1
        rst = cache.zrevrange(group_message_list_key, start, end, True)
        data = []
        for d in rst:
            message_id = d[0]
            amount = d[1]
            message = GroupMessage.get(message_id)
            if message:
                data.append({
                    'message_id': message.id,
                    'content': message.content,
                    'amount': amount,
                })

        return data



