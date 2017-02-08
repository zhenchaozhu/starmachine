# coding: utf-8

import logging
from datetime import datetime

from starmachine.lib.query import DbManager


logger = logging.getLogger(__name__)

class UserAuth(object):

    table = 'user_auth'

    def __init__(self, id=None, user_id=None, access_token=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.access_token = access_token
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<UserAuth:id=%s>' % (self.id)

    @classmethod
    def add(cls, user_id, access_token):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (user_id, access_token, create_time) values (%s, %s, %s)'.format(table=cls.table)
        try:
            user_auth_id = db.execute(sql, user_id, access_token, create_time)
            logger.info(u'添加用户access_token成功。user_auth_id:[%s]' % user_auth_id)
            return user_auth_id
        except Exception as e:
            logger.error(u'添加用户access_token失败。user_id:[%s], error:[%s]' % (user_id, e))
            raise

    @classmethod
    def get_by_user_id(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        user_auth_info = db.get(sql, user_id)
        return user_auth_info and cls(**user_auth_info)

    @classmethod
    def get_by_user_token(cls, token):
        db = DbManager().db
        sql = 'select * from {table} where access_token=%s'.format(table=cls.table)
        user_auth_info = db.get(sql, token)
        return user_auth_info and cls(**user_auth_info)

    @classmethod
    def update_access_token(cls, user_id, access_token):
        update_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set access_token=%s, update_time=%s where user_id=%s'.format(table=cls.table)
        return db.execute(sql, access_token, update_time, user_id)

    def clear_access_token(self):
        db = DbManager().db
        sql = 'update {table} set access_token=%s where id=%s'.format(table=self.table)
        return db.execute(sql, '', self.id)
