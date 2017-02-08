# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import STATUS_PENDING, ORDER_CHARGE, VALID_STATUS, STATUS_COMPLETE, PAYMETHOD_WEIXIN, WALLET_RECORD_CHARGE
from starmachine.model.order import Order
from starmachine.model.order.trade import Trade
from starmachine.model.account import Account
from starmachine.model.user import User
from starmachine.model.wallet_record import WalletRecord
from starmachine.model.order import Order
from starmachine.model.wxpay import WxPay
from starmachine.lib.utils import init_trade_id

class ChargeOrder(object):

    table = 'charge_order'

    def __init__(self, id=None, creator_id=None, amount=None, status=None, create_time=None, pay_time=None):
        self.id = id
        self.creator_id = creator_id
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.pay_time = pay_time

    def __repr__(self):
        return '<ChargeOrder:id=%s>' % (self.id)

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def trades(self):
        return Trade.gets_by_order_and_type(self.id, ORDER_CHARGE)

    @classmethod
    def add(cls, creator_id, amount, order_type, pay_method, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, amount, status, create_time) ' \
                'values (%s, %s, %s, %s)'.format(table=cls.table)
            order_id = db.execute(sql, creator_id, amount, status, create_time)
            trade_id = init_trade_id()
            sql = 'insert into {table} (id, order_id, order_type, amount, pay_method, status, create_time) values ' \
                  '(%s, %s, %s, %s, %s, %s, %s)'.format(table=Trade.table)
            db.execute(sql, trade_id, order_id, order_type, amount, pay_method, status, create_time)
            db.execute('commit;')
            return cls.get(order_id)
        except:
            db.execute('rollback;')
            raise

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        charge_order_info = db.get(sql, id)
        return charge_order_info and cls(**charge_order_info)

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        charge_orders = db.query(sql)
        return charge_orders and [cls(**charge_order) for charge_order in charge_orders]

    def receive_trade_payment(self):
        db = DbManager().db
        trades = self.trades
        now = datetime.now()
        all_trade_payed = True
        amount = float(self.amount)
        for trade in trades:
            if trade.status != STATUS_COMPLETE:
                all_trade_payed = False

        if all_trade_payed:
            db.execute('begin;')
            try:
                sql = 'update {table} set balance=balance+%s where user_id=%s'.format(table=Account.table)
                db.execute(sql, amount, self.creator_id)
                sql = 'update {table} set status=%s, pay_time=%s where id=%s'.format(table=self.table)
                db.execute(sql, STATUS_COMPLETE, now, self.id)
                sql = 'insert into {table} (user_id, source, order_type, order_id, amount, create_time) values ' \
                    '(%s, %s, %s, %s, %s, %s)'.format(table=WalletRecord.table)
                db.execute(sql, self.creator_id, WALLET_RECORD_CHARGE, ORDER_CHARGE, self.id, amount, now)
                db.execute('commit;')
            except:
                db.execute('rollback;')
                raise

    def complete(self):
        db = DbManager().db
        sql = 'update {table} set status=%s, pay_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, STATUS_COMPLETE, datetime.now())

    def jsonify(self):
        trades = self.trades
        data = {
            'id': self.id,
            'creator_id': self.creator_id,
            'amount': float(self.amount),
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'trades_info': [trade.jsonify() for trade in trades if trade],
        }

        return data
