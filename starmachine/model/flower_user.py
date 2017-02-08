# coding: utf-8

from datetime import datetime
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.query import DbManager
from starmachine.lib.utils import init_pic_url
from starmachine.model.group_seeds import GroupSeeds
from starmachine.model.group_envelope import GroupEnvelope

flower_user_name_update_limit_key = 'user:%s:group_name:update' # 30天清空一次
flower_user_name_update_limit_time = 30*24*60*60

class FlowerUser(object):

    table = 'flower_user'

    def __init__(self, id=None, user_id=None, name=None, avatar=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.avatar = avatar
        self.create_time = create_time
        self.update_time = update_time

    @property
    def avatar_url(self):
        return init_pic_url(self.avatar)

    @property
    def user_name(self):
        return self.name

    @classmethod
    def add(cls, user_id, name, avatar=''):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, name, avatar, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        id = db.execute(sql, user_id, name, avatar, create_time)
        return cls(id, user_id, name, avatar, create_time, None)

    @classmethod
    def get_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        return rst and cls(**rst)

    @classmethod
    def exists_name(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        rst = db.get(sql, name)
        return bool(rst)

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        r = db.execute(sql)
        return r

    def update_name(self, name):
        update_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set name=%s, update_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, name, update_time, self.id)

    def left_change_times(self):
        cache = CacheManager().cache
        redis_key = flower_user_name_update_limit_key % self.user_id
        if cache.exists(redis_key):
            update_count = cache.get(redis_key)
            return 3 - int(update_count)
        else:
            return 3

    def jsonify(self):
        return {
            'userId': self.user_id,
            'name': self.name,
            'portraitUri': self.avatar_url,
            'left_change_times': self.left_change_times(),
            'group_seeds': GroupSeeds.get_seeds_amount_by_user(self.user_id),
            'group_envelope': GroupEnvelope.get_envelope_amount_by_user(self.user_id),
        }