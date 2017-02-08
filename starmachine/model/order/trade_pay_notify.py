# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager

class TradePayNotify(object):

    table = 'trade_pay_notify'

    def __init__(self, id=None, trade_id=None, pay_method=None, notify=None, create_time=None, update_time=None):
        self.id = id
        self.trade_id = trade_id
        self.pay_method = pay_method
        self.notify = notify
        self.create_time = create_time
        self.update_time = update_time

    @classmethod
    def add(cls, trade_id, pay_method, notify):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (trade_id, pay_method, notify, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        order_pay_notify_id = db.execute(sql, trade_id, pay_method, notify, create_time)
        return order_pay_notify_id