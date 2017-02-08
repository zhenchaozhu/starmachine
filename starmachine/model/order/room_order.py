# coding: utf-8

import calendar
from datetime import datetime, timedelta
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.utils import redis_cache_amount, init_trade_id
from starmachine.model.order.trade import Trade, InvalidStatusException
from starmachine.model.consts import ORDER_ROOM, STATUS_PENDING, STATUS_COMPLETE, PAYMETHOD_ACCOUNT, VALID_STATUS, WALLET_RECORD_ROOM_RENT
from starmachine.model.account import Account
from starmachine.model.star_fund import StarFund
from starmachine.model.room_user import RoomUser
from starmachine.model.wallet_record import WalletRecord

ROOM_DATE_FUND_CACHE = 'room:%s:date:%s:fund'

class RoomOrder(object):

    table = 'room_order'

    def __init__(self, id, creator_id, room_id, amount, status, create_time, pay_time, refund_time):
        self.id = id
        self.creator_id = creator_id
        self.room_id = room_id
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.pay_time = pay_time
        self.refund_time = refund_time

    @property
    def trades(self):
        return Trade.gets_by_order_and_type(self.id, ORDER_ROOM)

    @classmethod
    def add(cls, creator_id, room_id, amount, trades_info, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, room_id, amount, status, create_time) values (%s, %s, %s, %s, %s)'\
                .format(table=cls.table)
            room_order_id = db.execute(sql, creator_id, room_id, amount, status, create_time)
            for trade_info in trades_info:
                trade_id = init_trade_id()
                amount = trade_info.get('amount')
                pay_method = trade_info.get('pay_method')
                sql = 'insert into {table} (id, order_id, order_type, amount, pay_method, status, create_time) ' \
                    'values (%s, %s, %s, %s, %s, %s, %s)'.format(table=Trade.table)
                db.execute(sql, trade_id, room_order_id, ORDER_ROOM, amount, pay_method, status, create_time)
            db.execute('commit;')
            return cls(room_order_id, creator_id, room_id, amount, status, create_time, None, None)
        except Exception:
            db.execute('rollback;')
            raise

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        room_order_info = db.get(sql, id)
        return room_order_info and cls(**room_order_info)

    @classmethod
    def get_by_room_and_user(cls, room_id, user_id):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
        room_order_info = db.get(sql, room_id, user_id)
        return room_order_info and cls(**room_order_info)

    @classmethod
    @redis_cache_amount(ROOM_DATE_FUND_CACHE)
    def get_fund_amount_by_room_and_month(cls, room_id, date):
        db = DbManager().db
        sql = 'select sum(amount) from {table} where status=%s and room_id=%s and pay_time < %s'.format(table=cls.table)
        rst = db.get(sql, STATUS_COMPLETE, room_id, date)
        if rst and rst.get('sum(amount)'):
            return float(rst.get('sum(amount)'))
        else:
            return 0

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        reward_orders = db.query(sql)
        return reward_orders and [cls(**reward_order) for reward_order in reward_orders]

    def update(self, **kwargs):
        db = DbManager().db
        if 'status' in kwargs and kwargs['status'] not in VALID_STATUS:
            raise InvalidStatusException
        invalid_fields = ('id')
        for field in invalid_fields:
            if field in kwargs:
                del kwargs[field]

        sql = 'update {table} set '.format(table=self.table) +\
             ','.join('%s=%s' % (k, kwargs.get(k)) for k in kwargs) + ' where id=%s'
        r = db.execute(sql, self.id)
        return r

    def receive_trade_payment(self):
        db = DbManager().db
        trades = self.trades
        now = datetime.now()
        all_trades_complete = True
        for trade in trades:
            if trade.status != STATUS_COMPLETE:
                return

        if all_trades_complete:
            try:
                db.execute('begin;')
                for trade in trades:
                    if trade.pay_method == PAYMETHOD_ACCOUNT:
                        sql = 'update {table} set balance=balance-%s where user_id=%s'.format(table=Account.table)
                        db.execute(sql, float(trade.amount), self.creator_id)
                sql = 'update {table} set balance=balance+%s where room_id=%s'.format(table=StarFund.table)
                db.execute(sql, float(self.amount), self.room_id)
                sql = 'update {table} set status=%s, pay_time=%s where id=%s'.format(table=self.table)
                db.execute(sql, STATUS_COMPLETE, now, self.id)
                sql = 'insert into {table} (user_id, source, order_type, order_id, amount, create_time) values ' \
                      '(%s, %s, %s, %s, %s, %s)'.format(table=WalletRecord.table)
                db.execute(sql, self.creator_id, WALLET_RECORD_ROOM_RENT, ORDER_ROOM, self.id, -self.amount, now)
                db.execute('commit;')
            except:
                db.execute('rollback;')
                raise

        RoomUser.add(self.room_id, self.creator_id)
        self.flush_fund_cache()

    def flush_fund_cache(self):
        cache = CacheManager().cache
        now = datetime.now()
        for delta in xrange(1, 5):
            month = now.month - 1 + delta
            year = now.year + month / 12
            month = month % 12 + 1
            max_day = calendar.monthrange(year, month)[1]
            end_day = (datetime(year=year, month=month, day=max_day) + timedelta(days=1)).strftime('%Y-%m-%d')
            room_cache_key = ROOM_DATE_FUND_CACHE % (self.room_id, end_day)
            cache.delete(room_cache_key)

    def complete(self):
        self.update(self.id, status=STATUS_COMPLETE, pay_time=datetime.now())

    def jsonify(self):
        data = {
            'id': self.id,
            'creator_id': self.creator_id,
            'room_id': self.room_id,
            'amount': float(self.amount),
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        trades = Trade.gets_by_order_and_type(self.id, ORDER_ROOM)
        trades_info = []
        for trade in trades:
            trades_info.append(trade.jsonify())

        data['trades_info'] = trades_info
        return data