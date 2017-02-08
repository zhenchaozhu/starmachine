# coding: utf-8

from starmachine.lib.query import DbManager
from starmachine.lib.utils import redis_cache_obj

ACCOUNT_CACHE_KEY = 'account:%s'

class Account(object):

    table = 'account'

    def __init__(self, id=None, user_id=None, balance=None):
        self.id = id
        self.user_id = user_id
        self.balance = balance

    def __repr__(self):
        return '<Account:id=%s>' % (self.id)

    @classmethod
    def add(cls, user_id, balance=0.00):
        db = DbManager().db
        sql = 'insert into {table} (user_id, balance) values (%s, %s)'.format(table=cls.table)
        account_id = db.execute(sql, user_id, balance)
        return account_id and cls(id=account_id, user_id=user_id, balance=balance)

    @classmethod
    def get_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        account_info = db.get(sql, user_id)
        return account_info and cls(**account_info)

    def add_balance(self, balance):
        db = DbManager().db
        sql = 'update {table} set balance=balance+%s where user_id=%s'.format(table=self.table)
        db.execute(sql, balance, self.user_id)

    def jsonify(self):
        return {
            'user_id': self.user_id,
            'balance': float(self.balance)
        }

