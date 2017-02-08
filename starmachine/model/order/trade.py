# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.order import InvalidStatusException
from starmachine.model.consts import STATUS_PENDING, STATUS_COMPLETE, ORDER_CHARGE, ORDER_ROOM, VALID_STATUS, \
    PAYMETHOD_ACCOUNT, ORDER_REWARD, PAYMETHOD_WEIXIN, PAYMETHOD_ALIPAY
from starmachine.model.account import Account
from starmachine.model.order import AccountBalanceNotEnoughException

class Trade(object):

    table = 'trade'

    def __init__(self, id=None, order_id=None, order_type=None, amount=None, pay_method=None, status=None, create_time=None,
        pay_time=None, refund_time=None):
        self.id = id
        self.order_id = order_id
        self.order_type = order_type
        self.amount = amount
        self.pay_method = pay_method
        self.status = status
        self.create_time = create_time
        self.pay_time = pay_time
        self.refund_time = refund_time

    @property
    def order(self):
        from starmachine.model.order.charge import ChargeOrder
        from starmachine.model.order.room_order import RoomOrder
        from starmachine.model.order.reward_order import RewardOrder
        ORDER_CLASS_MAP = {
            ORDER_CHARGE: ChargeOrder,
            ORDER_ROOM: RoomOrder,
            ORDER_REWARD: RewardOrder,
        }
        order_model= ORDER_CLASS_MAP.get(self.order_type)
        return order_model.get(self.order_id)

    @classmethod
    def add(cls, order_id, order_type, amount, pay_method, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (order_id, order_type, amount, pay_method, status, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        trade_id = db.execute(sql, order_id, order_type, amount, pay_method, status, create_time)
        return trade_id

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        trade_info = db.get(sql, id)
        return trade_info and cls(**trade_info)

    def update(self, **kwargs):
        db = DbManager().db
        if 'status' in kwargs and kwargs['status'] not in VALID_STATUS:
            raise InvalidStatusException
        invalid_fields = ('id',)
        for field in invalid_fields:
            if field in kwargs:
                del kwargs[field]

        sql = 'update {table} set '.format(table=self.table) + ','.join('%s="%s"' % (k, kwargs.get(k)) for k in kwargs)\
             + ' where id=%s'
        r = db.execute(sql, self.id)
        return r

    @classmethod
    def gets_by_order_and_type(cls, order_id, order_type):
        db = DbManager().db
        sql = 'select * from {table} where order_id=%s and order_type=%s'.format(table=cls.table)
        trades = db.query(sql, order_id, order_type)
        return trades and [cls(**trade) for trade in trades]

    def receive_pay(self):
        order = self.order
        if self.pay_method in (PAYMETHOD_WEIXIN, PAYMETHOD_ALIPAY):
            trades = order.trades
            for trade in trades:
                if trade.pay_method == PAYMETHOD_ACCOUNT and trade.status == STATUS_PENDING:
                    trade.complete()

        self.complete()
        order.receive_trade_payment()

    def complete(self):
        self.update(status=STATUS_COMPLETE, pay_time=datetime.now())

    def refund(self, refund_time):
        self.update(status=STATUS_COMPLETE, refund_time=refund_time)

    def jsonify(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_type': self.order_type,
            'amount': float(self.amount),
            'pay_method': self.pay_method,
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }


