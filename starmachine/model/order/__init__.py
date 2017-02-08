# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import STATUS_PENDING
from starmachine.model.user import User


class Order(object):

    table = 'order'

    def __init__(self, id, creator_id, amount, order_id, order_type, status, create_time, pay_time, refund_time):
        self.id = id
        self.creator_id = creator_id
        self.amount = amount
        self.order_id = order_id
        self.order_type = order_type
        self.status = status
        self.create_time = create_time
        self.pay_time = pay_time
        self.refund_time = refund_time

    @property
    def creator(self):
        return User.get(self.creator_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        order_info = db.get(sql, id)
        return order_info and cls(**order_info)

    def jsonify(self):
        from starmachine.model.order.charge import ChargeOrder
        return {
            'id': self.id,
            'creator': self.creator.jsonify(),
            'amount': float(self.amount),
            'order_type': self.order_type,
            'status': self.status
        }


class InvalidStatusException(Exception):
    pass

class AccountBalanceNotEnoughException(Exception):
    pass
