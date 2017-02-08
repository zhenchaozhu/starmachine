# coding: utf-8

import logging
from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.utils import init_pic_url
from starmachine.lib.redis_cache import CacheManager
from starmachine.rong.rong_client import rong_client
from starmachine.model.user import User
from starmachine.model.consts import GROUP_USER_CREATOR, GROUP_USER_CACHE_KEY, USER_GROUP_CACHE_KEY, GROUP_USER_COUNT_KEY
from starmachine.model.group_user import GroupUser
from starmachine.model.group_message_liked import GroupMessageLiked
from starmachine.model.flower_user import FlowerUser
from starmachine.model.rong import UserChatStatus
from starmachine.model.group_user import GroupBlackUser

DEFAULT_LIMIT_USER = 500

logger = logging.getLogger(__name__)

class Group(object):

    table = 'rong_group'

    def __init__(self, id=None, creator_id=None, avatar=None, name=None, announcement=None, limit_user=None,
        create_time=None, update_time=None):
        self.id = id
        self.creator_id = creator_id
        self.avatar = avatar
        self.name = name
        self.announcement = announcement
        self.limit_user = limit_user
        self.create_time = create_time
        self.update_time = update_time

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def user_amount(self):
        return GroupUser.get_user_amount_by_group(self.id)

    @property
    def avatar_url(self):
        return init_pic_url(self.avatar)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, creator_id, avatar, name, announcement='', limit_user=DEFAULT_LIMIT_USER):
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, avatar, name, announcement, limit_user, create_time) values (%s, ' \
            '%s, %s, %s, %s, %s)'.format(table=cls.table)
            group_id = db.execute(sql, creator_id, avatar, name, announcement, limit_user, create_time)
            # sql = 'insert into {table} (group_id, user_id, status, join_time) values (%s, %s, %s, %s)'.\
            # format(table=GroupUser.table)
            # db.execute(sql, group_id, creator_id, GROUP_USER_CREATOR, create_time)
            rong_client.group_create([creator_id], group_id, name)
            db.execute('commit;')
        except Exception:
            db.execute('rollback;')
            raise

        GroupUser.add_group_user(group_id, name, creator_id, GROUP_USER_CREATOR)
        return cls(group_id, creator_id, avatar, name, announcement, limit_user, create_time, None)

    @classmethod
    def get_groups_by_user(cls, user_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where creator_id=%s limit %s, %s'.format(table=cls.table)
        rst = db.query(sql, user_id, start, count)
        return rst and [cls(**d) for d in rst]

    @classmethod
    def get_groups_order_by_user_amount(cls, start=0, count=10):
        cache = CacheManager().cache
        end = start + count - 1
        rank_key = 'group:user:count'
        group_ids = cache.zrevrange(rank_key, start, end)
        return group_ids and [Group.get(group_id) for group_id in group_ids]

    @classmethod
    def search_group(cls, query, start, count):
        db = DbManager().db
        sql = 'select * from {table} where name like %s limit %s, %s'.format(table=cls.table)
        q = '%' + query + '%'
        rst = db.query(sql, q, start, count)
        return rst and [cls(**d) for d in rst]

    @classmethod
    def is_over_create_limit(cls, user_id):
        db = DbManager().db
        sql = 'select count(id) from {table} where creator_id=%s'.format(table=cls.table)
        count = db.get(sql, user_id)
        return count.get('count(id)') >= 3

    @classmethod
    def exists_group(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None

    def delete(self):
        db = DbManager().db
        cache = CacheManager().cache
        sql = 'delete from {table} where id=%s'.format(table=self.table)
        db.execute(sql, self.id)
        sql = 'delete from {table} where group_id=%s'.format(table=GroupUser.table)
        db.execute(sql, self.id)
        group_user_cache_key = GROUP_USER_CACHE_KEY % self.id
        user_ids = cache.zrevrange(group_user_cache_key, 0, -1)
        for user_id in user_ids:
            user_group_cache_key = USER_GROUP_CACHE_KEY % user_id
            cache.zrem(user_group_cache_key, self.id)
        cache.delete(group_user_cache_key)
        cache.zrem(GROUP_USER_COUNT_KEY, self.id)

    def exists_user(self, user_id):
        cache = CacheManager().cache
        group_user_key = 'group:%s:user' % self.id
        return cache.zscore(group_user_key, user_id) != None

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        r = db.execute(sql)
        return r


    def jsonify(self, user=None):
        creator = self.creator
        result = {
            'groupId': str(self.id),
            'groupName': self.name,
            'portraitUri': init_pic_url(self.avatar),
            'announcement': self.announcement,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_amount': self.user_amount,
            'is_full': False if self.user_amount < DEFAULT_LIMIT_USER else True,
        }
        if UserChatStatus.is_flower_identity(creator.id):
            creator_obj = FlowerUser.get_by_user(creator.id).jsonify()
        else:
            creator_obj = {
                'userId': str(self.creator.id),
                'name': self.creator.user_name,
                'portraitUri': self.creator.avatar_url,
            }

        result.update({
            'creator': creator_obj,
        })
        group_user_ids = GroupUser.get_users_by_group(self.id, 0, 10)
        group_users = []
        for user_id in group_user_ids:
            if UserChatStatus.is_flower_identity(user_id):
                group_user = FlowerUser.get_by_user(user_id)
            else:
                group_user = User.get(user_id)

            group_users.append({
                'userId': user_id,
                'name': group_user.user_name,
                'portraitUri': group_user.avatar_url,
            })

        result.update({
            'users': group_users,
        })
        if user:
            result.update({
                'has_joined': True if self.exists_user(user.id) else False,
                'is_black': bool(GroupBlackUser.is_group_black_user(self.id, user.id)),
            })

        return result


class GroupVoiceTime(object):

    table = 'group_voice_time'

    def __init__(self, id=None, group_id=None, user_id=None, voice_time=None):
        self.id = id
        self.group_id = group_id
        self.user_id = user_id
        self.voice_time = voice_time

    @classmethod
    def get_by_group_and_user(cls, group_id, user_id):
        db = DbManager().db
        sql = 'select * from {table} where group_id=%s and user_id=%s'.format(table=cls.table)
        rst = db.get(sql, group_id, user_id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, group_id, user_id):
        voice_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (group_id, user_id, voice_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, group_id, user_id, voice_time)

    def update_voice_time(self):
        voice_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set voice_time=%s'.format(table=self.table)
        db.execute(sql, voice_time)

