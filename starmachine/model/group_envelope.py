# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.account import Account
from starmachine.model.consts import STATUS_PENDING, STATUS_COMPLETE, WALLET_RECORD_GROUP_CHAT_REWARD, ORDER_GROUP_ENVELOPE

class GroupReward(object):

    table = 'group_reward'

    def __init__(self, id, receiver_id, group_id, message_id, liked_amount, reward_type):
        self.id = id
        self.receiver_id = receiver_id
        self.group_id = group_id
        self.message_id = message_id
        self.liked_amount = liked_amount
        self.reward_type = reward_type

    @classmethod
    def add(cls, receiver_id, group_id, message_id, liked_amount, reward_type):
        db = DbManager().db
        sql = 'insert into {table} (receiver_id, group_id, message_id, liked_amount, reward_type) values (%s, %s, %s, %s, %s)'.format(table=cls.table)
        envelope_id = db.execute(sql, receiver_id, group_id, message_id, liked_amount, reward_type)
        return cls(envelope_id, receiver_id, group_id, message_id, liked_amount, reward_type)

    @classmethod
    def has_get_reward(cls, group_id, message_id, liked_amount):
        db = DbManager().db
        sql = 'select id from {table} where group_id=%s and message_id=%s and liked_amount=%s'.format(table=cls.table)
        rst = db.get(sql, group_id, message_id, liked_amount)
        return bool(rst)


class GroupEnvelope(object):

    table = 'group_envelope'

    def __init__(self, id, receiver_id, group_id, message_id, liked_amount, amount, status, create_time, receive_time):
        self.id = id
        self.receiver_id = receiver_id
        self.group_id = group_id
        self.message_id = message_id
        self.liked_amount = liked_amount
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.receive_time = receive_time

    @classmethod
    def add(cls, receiver_id, group_id, message_id, liked_amount, amount, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (receiver_id, group_id, message_id, liked_amount, amount, status, create_time) ' \
            'values (%s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        envelope_id = db.execute(sql, receiver_id, group_id, message_id, liked_amount, amount, status, create_time)
        return cls(envelope_id, receiver_id, group_id, message_id, liked_amount, amount, status, create_time, None)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def get_envelope_amount_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select count(id) from {table} where receiver_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        return rst and rst.get('count(id)')

    def receive(self):
        from starmachine.model.wallet_record import WalletRecord
        db = DbManager().db
        amount = float(self.amount)
        receive_time = datetime.now()
        try:
            db.execute('begin;')
            sql = 'update {table} set balance=balance+%s where user_id=%s'.format(table=Account.table)
            db.execute(sql, amount, self.receiver_id)
            sql = 'update {table} set status=%s, receive_time=%s where id=%s'.format(table=self.table)
            db.execute(sql, STATUS_COMPLETE, receive_time, self.id)
            sql = 'insert into {table} (user_id, source, order_type, order_id, amount, create_time) values ' \
                  '(%s, %s, %s, %s, %s, %s)'.format(table=WalletRecord.table)
            db.execute(sql, self.receiver_id, WALLET_RECORD_GROUP_CHAT_REWARD, ORDER_GROUP_ENVELOPE, self.id, self.amount, receive_time)
            db.execute('commit;')
        except Exception as e:
            db.execute('rollback;')
            raise

