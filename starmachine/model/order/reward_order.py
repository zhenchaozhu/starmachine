# coding: utf-8

import logging
import calendar
from datetime import datetime, timedelta
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.consts import STATUS_PENDING, ORDER_REWARD, STATUS_COMPLETE, PAYMETHOD_ACCOUNT, \
    CONTENT_REWARD_AMOUNT_CACHE_KEY, CONTENT_REWARD_CACHE_KEY, ROOM_USER_REWARD_CACHE_KEY, USER_REWARD_CONTENT_KEY, \
    USER_REWARD_RANK_CACHE_KEY, WALLET_RECORD_REWARD_SEND, WALLET_RECORD_REWARD_RECEIVE
from starmachine.model.order.trade import Trade
from starmachine.model.user import User
from starmachine.model.account import Account
from starmachine.lib.utils import get_int_date, init_trade_id
from starmachine.tools.postman import notify_content_reward
from starmachine.model.content import Content
from starmachine.model.wallet_record import WalletRecord
from starmachine.lib.utils import redis_cache_amount
from starmachine.jobs.integral import handle_daily_send_reward

USER_DATE_REWARD_CACHE = 'user:%s:date:%s:reward'
REWARD_TYPE_CONTENT = 1
REWARD_TYPE_CHAT = 2

class RewardOrder(object):

    table = 'reward_order'

    def __init__(self, id=None, creator_id=None, receiver_id=None, type=None, content_id=None, room_id=None, amount=None,
        status=None, create_time=None, pay_time=None):
        self.id = id
        self.creator_id = creator_id
        self.receiver_id = receiver_id
        self.type = type
        self.content_id = content_id
        self.room_id = room_id
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.pay_time = pay_time

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def receiver(self):
        return User.get(self.receiver_id)

    @property
    def trades(self):
        return Trade.gets_by_order_and_type(self.id, ORDER_REWARD)

    @classmethod
    def add(cls, creator_id, receiver_id, content_id, room_id, amount, trades_info, type=REWARD_TYPE_CONTENT, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, receiver_id, type, content_id, room_id, amount, status, create_time) ' \
                'values (%s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            reward_order_id = db.execute(sql, creator_id, receiver_id, type, content_id, room_id, amount, status, create_time)
            for trade_info in trades_info:
                trade_id = init_trade_id()
                pay_method = trade_info.get('pay_method')
                amount = trade_info.get('amount')
                sql = 'insert into {table} (id, order_id, order_type, amount, pay_method, status, create_time) values ' \
                    '(%s, %s, %s, %s, %s, %s, %s)'.format(table=Trade.table)
                db.execute(sql, trade_id, reward_order_id, ORDER_REWARD, amount, pay_method, status, create_time)
            db.execute('commit;')
            return cls(reward_order_id, creator_id, receiver_id, type, content_id, room_id, amount, status, create_time, None)
        except Exception:
            db.execute('rollback')
            raise

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        reward_order_info = db.get(sql, id)
        return reward_order_info and cls(**reward_order_info)

    @classmethod
    @redis_cache_amount(USER_DATE_REWARD_CACHE)
    def get_reward_amount_by_user_and_date(cls, user_id, date):
        db = DbManager().db
        sql = 'select sum(amount) from {table} where status=%s and receiver_id=%s and pay_time < %s'.format(table=cls.table)
        rst = db.get(sql, STATUS_COMPLETE, user_id, date)
        if rst and rst.get('sum(amount)'):
            return float(rst.get('sum(amount)'))
        else:
            return 0

    @classmethod
    def get_user_receive_reward_amount(cls, user_id):
        db = DbManager().db
        sql = 'select sum(amount) from {table} where status=%s and receiver_id=%s'.format(table=cls.table)
        rst = db.get(sql, STATUS_COMPLETE, user_id)
        if rst and rst.get('sum(amount)'):
            return float(rst.get('sum(amount)'))
        else:
            return 0

    @classmethod
    def get_reward_orders_by_content(cls, content_id, start=0, count=10):
        cache = CacheManager().cache
        cache_key = CONTENT_REWARD_CACHE_KEY % content_id
        end = start + count - 1
        reward_ids = cache.lrange(cache_key, start, end)
        return reward_ids and [RewardOrder.get(reward_id) for reward_id in reward_ids]

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        infos = db.query(sql)
        return infos and [cls(**info) for info in infos]

    @classmethod
    def get_user_reward_rank(cls, start=0, count=10):
        cache = CacheManager().cache
        end = start + count - 1
        rst = cache.zrevrange(USER_REWARD_RANK_CACHE_KEY, start, end, True)
        if rst:
            return [{'user_id': d[0], 'amount': d[1]} for d in rst]
        else:
            return []

    @classmethod
    def get_reward_orders_by_receiver(cls, receiver_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where receiver_id=%s and status=%s order by create_time limit %s, %s'.format(table=cls.table)
        reward_orders = db.query(sql, receiver_id, STATUS_COMPLETE, start, count)
        return reward_orders and [cls(**reward_order) for reward_order in reward_orders]

    def receive_trade_payment(self):
        db = DbManager().db
        cache = CacheManager().cache
        trades = self.trades
        now = datetime.now()
        score = get_int_date(now)
        all_trades_complete = True
        for trade in trades:
            if trade.status != STATUS_COMPLETE:
                all_trades_complete = False
                break

        if all_trades_complete:
            try:
                db.execute('begin;')
                for trade in trades:
                    if trade.pay_method == PAYMETHOD_ACCOUNT:
                        sql = 'update {table} set balance=balance-%s where user_id=%s'.format(table=Account.table)
                        db.execute(sql, float(trade.amount), self.creator_id)
                sql = 'update {table} set balance=balance+%s where user_id=%s'.format(table=Account.table)
                db.execute(sql, float(self.amount), self.receiver_id)
                sql = 'update {table} set status=%s, pay_time=%s where id=%s'.format(table=self.table)
                db.execute(sql, STATUS_COMPLETE, now, self.id)
                sql = 'insert into {table} (user_id, source, order_type, order_id, amount, create_time) values ' \
                      '(%s, %s, %s, %s, %s, %s)'.format(table=WalletRecord.table)
                db.execute(sql, self.creator_id, WALLET_RECORD_REWARD_SEND, ORDER_REWARD, self.id, -self.amount, now)
                db.execute(sql, self.receiver_id, WALLET_RECORD_REWARD_RECEIVE, ORDER_REWARD, self.id, self.amount, now)
                db.execute('commit;')
            except:
                db.execute('rollback;')
                raise

            notify_content_reward.delay(self.creator, Content.get(self.content_id), self)
            cache.zincrby(CONTENT_REWARD_AMOUNT_CACHE_KEY, self.content_id, float(self.amount) * 100)
            cache_key = ROOM_USER_REWARD_CACHE_KEY % self.room_id
            cache.zincrby(cache_key, self.creator_id, float(self.amount) * 100)
            cache_key = USER_REWARD_RANK_CACHE_KEY
            cache.zincrby(cache_key, self.creator_id, float(self.amount) * 100)
            cache_key = CONTENT_REWARD_CACHE_KEY % self.content_id
            cache.lpush(cache_key, self.id)
            cache.zadd(USER_REWARD_CONTENT_KEY % self.creator_id, score, self.content_id)
            self.flush_reward_cache()
            handle_daily_send_reward.delay(self)

    def flush_reward_cache(self):
        cache = CacheManager().cache
        now = datetime.now()
        for delta in xrange(1, 5):
            month = now.month - 1 + delta
            year = now.year + month / 12
            month = month % 12 + 1
            max_day = calendar.monthrange(year, month)[1]
            end_day = (datetime(year=year, month=month, day=max_day) + timedelta(days=1)).strftime('%Y-%m-%d')
            user_cache_key = USER_DATE_REWARD_CACHE % (self.room_id, end_day)
            cache.delete(user_cache_key)

    def jsonify(self):
        data = {
            'id': self.id,
            'creator_id': self.creator_id,
            'receiver_id': self.receiver_id,
            'type': self.type,
            'content_id': self.content_id,
            'room_id': self.room_id,
            'amount': float(self.amount),
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        trades = Trade.gets_by_order_and_type(self.id, ORDER_REWARD)
        trades_info = []
        for trade in trades:
            trades_info.append(trade.jsonify())

        data['trades_info'] = trades_info
        return data


