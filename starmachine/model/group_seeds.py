# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.account import Account
from starmachine.model.consts import STATUS_PENDING, STATUS_COMPLETE

class GroupSeeds(object):

    table = 'group_seeds'

    def __init__(self, id, receiver_id, group_id, message_id, liked_amount, amount, create_time):
        self.id = id
        self.receiver_id = receiver_id
        self.group_id = group_id
        self.message_id = message_id
        self.liked_amount = liked_amount
        self.amount = amount
        self.create_time = create_time

    @classmethod
    def add(cls, receiver_id, group_id, message_id, liked_amount, amount):
        db = DbManager().db
        create_time = datetime.now()
        try:
            db.execute('begin;')
            sql = 'insert into {table} (receiver_id, group_id, message_id, liked_amount, amount, create_time) values' \
                ' (%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            seeds_id = db.execute(sql, receiver_id, group_id, message_id, liked_amount, amount, create_time)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        return cls(seeds_id, receiver_id, group_id, message_id, liked_amount, amount, create_time)

    @classmethod
    def get_seeds_amount_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select sum(amount) from {table} where receiver_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        amount = rst.get('sum(amount)')
        if not amount:
            return 0
        else:
            return int(amount)