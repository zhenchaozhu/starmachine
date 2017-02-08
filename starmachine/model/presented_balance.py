# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager

class PresentedBalance(object):

    table = 'presented_balance'

    def __init__(self, id=None, user_id=None, amount=None, type=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.type = type
        self.create_time = create_time

    @classmethod
    def add(cls, user_id, balance, type):
        db = DbManager().db
        now = datetime.now()
        sql = 'insert into {table} (user_id, amount, type, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, balance, type, now)