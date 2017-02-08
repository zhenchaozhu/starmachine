# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import CHAT_FLOWER_IDENTITY

class RongToken(object):

    table = 'rong_token'

    def __init__(self, id=None, user_id=None, token=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.token = token
        self.create_time = create_time

    @classmethod
    def add(cls, user_id, token):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, token, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, token, create_time)

    @classmethod
    def get_rong_token_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        return rst and cls(**rst)


class UserChatStatus(object):

    table = 'user_chat_status'

    def __init__(self, id=None, user_id=None, status=None):
        self.id = id
        self.user_id = user_id
        self.status = status

    @classmethod
    def add(cls, user_id, status):
        db = DbManager().db
        sql = 'insert into {table} (user_id, status) values (%s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, status)

    @classmethod
    def get_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        return rst and cls(**rst)

    @classmethod
    def is_flower_identity(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        if rst:
            status = cls(**rst).status
            return int(status) == CHAT_FLOWER_IDENTITY

        return False

    def update(self, status):
        db = DbManager().db
        sql = 'update {table} set status=%s where id=%s'.format(table=self.table)
        db.execute(sql, status, self.id)


