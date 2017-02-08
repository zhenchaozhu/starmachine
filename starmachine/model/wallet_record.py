# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.user import User

class WalletRecord(object):

    table = 'wallet_record'

    def __init__(self, id=None, user_id=None, source=None, order_type=None, order_id=None, amount=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.source = source
        self.order_type = order_type
        self.order_id = order_id
        self.amount = amount
        self.create_time = create_time

    @property
    def user(self):
        return User.get(self.user_id)

    @classmethod
    def add(cls, user_id, source, order_type, order_id, amount, create_time):
        db = DbManager().db
        sql = 'insert into {table} (user_id, source, order_type, order_id, amount, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, source, order_type, order_id, amount, create_time)

    @classmethod
    def gets_by_user(cls, user_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s order by create_time desc limit %s, %s'.format(table=cls.table)
        records = db.query(sql, user_id, start, count)
        return records and [cls(**record) for record in records]

    def jsonify(self):
        return {
            'id': self.id,
            'user': {
                'id': self.user.id,
                'name': self.user.user_name,
                'avatar': self.user.avatar_url,
            },
            'source': self.source,
            'amount': float(self.amount),
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

