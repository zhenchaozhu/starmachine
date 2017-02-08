# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.utils import init_trade_id
from starmachine.model.consts import STATUS_PENDING, ORDER_ACTIVITY, STATUS_COMPLETE, PAYMETHOD_ACCOUNT, STATUS_REFUNDED
from starmachine.model.order.trade import Trade
from starmachine.model.account import Account
from starmachine.model.star_fund import StarFund
from starmachine.model.content.activity import Activity, ActivityAccount, ActivityResult
from starmachine.handlers.exception import AccountBalanceInsufficient, StarFundInsufficient

class ActivityOrder(object):

    table = 'activity_order'

    def __init__(self, id, creator_id, activity_id, option_id, user_address_id, amount, status, create_time, pay_time, refund_time):
        self.id = id
        self.creator_id = creator_id
        self.activity_id = activity_id
        self.option_id = option_id
        self.user_address_id = user_address_id
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.pay_time = pay_time
        self.refund_time = refund_time

    @property
    def trades(self):
        return Trade.gets_by_order_and_type(self.id, ORDER_ACTIVITY)

    @classmethod
    def add(cls, creator_id, activity_id, option_id, user_address_id, amount, trades_info, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, activity_id, option_id, user_address_id, amount, status, create_time) values ' \
                '(%s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            activity_order_id = db.execute(sql, creator_id, activity_id, option_id, user_address_id, amount, status, create_time)
            for trade_info in trades_info:
                trade_id = init_trade_id()
                amount = trade_info.get('amount')
                pay_method = trade_info.get('pay_method')
                sql = 'insert into {table} (id, order_id, order_type, amount, pay_method, status, create_time) values ' \
                    '(%s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
                db.execute(sql, trade_id, activity_order_id, ORDER_ACTIVITY, amount, pay_method, status, create_time)
            db.execute('commit;')
            return cls(activity_order_id, creator_id, activity_id, amount, status, create_time, None, None)
        except:
            db.execute('rollback;')
            raise

    @classmethod
    def get_by_option_and_user(cls, option_id, user_id):
        db = DbManager().db
        sql = 'select * from {table} where option_id=%s and user_id=%s'.format(table=cls.table)
        order_info = db.get(sql, option_id, user_id)
        return order_info and cls(**order_info)

    @classmethod
    def gets_complete_order_by_activity(cls, activity_id):
        db = DbManager().db
        sql = 'select * from {table} where activity_id=%s and status=%s'.format(table=cls.table)
        orders_info = db.query(sql, activity_id, STATUS_COMPLETE)
        return orders_info and [cls(**order_info) for order_info in orders_info]

    def receive_trade_payment(self):
        db = DbManager().db
        activity = Activity.get(self.activity_id)
        account = Account.get_by_user(self.creator_id)
        star_fund = StarFund.get_by_room(activity.room_id)
        trades = self.trades
        now = datetime.now()
        all_trades_complete = True
        for trade in trades:
            if trade.status != STATUS_COMPLETE:
                all_trades_complete = False
                break

        if all_trades_complete:
            try:
                db.execute('begin;')
                for trade in trades:
                    # 如果是余额支付，则从用户账户中扣除余额
                    if trade.pay_method == PAYMETHOD_ACCOUNT:
                        # 如果余额不够或者房基金不够则退出
                        if float(account.balance) < float(trade.amount):
                            raise AccountBalanceInsufficient
                        # 扣除余额的钱
                        sql = 'update {table} set balance=balance-%s where user_id=%s'.format(table=Account.table)
                        db.execute(sql, float(trade.amount), self.creator_id)

                if float(star_fund.balance) < float(activity.discount):
                    raise StarFundInsufficient

                # 扣除房基金的钱
                sql = 'update {table} set balance=balance-%s where id=%s'.format(table=StarFund.table)
                db.execute(sql, float(activity.discount), star_fund.id)
                # 活动经费里面加上钱
                sql = 'update {table} set balance=balance+%s where id=%s'.format(table=StarFund.table)
                db.execute(sql, float(self.amount), self.activity_id)
                sql = 'update {table} set status=%s, pay_time=%s where id=%s'.format(table=self.table)
                db.execute(sql, STATUS_COMPLETE, now, self.id)
                db.execute('commit;')
            except:
                db.execute('rollback;')
                raise

            ActivityResult.add(self.activity_id, self.option_id, self.creator_id)

    def free_order_complete(self):
        db = DbManager().db
        sql = 'update {table} set status=%s where id=%s'.format(table=self.table)
        db.execute(sql, STATUS_COMPLETE, self.id)
        ActivityResult.add(self.activity_id, self.option_id, self.creator_id)

    def refund(self):
        # 免费的订单就不需要进行退款操作了
        db = DbManager().db
        db.execute('begin;')
        refund_time = datetime.now()
        amount = float(self.amount)
        if not amount:
            sql = 'update {table} set status=%s, refund_time=%s where id=%s'.format(table=self.table)
            db.execute(sql, STATUS_REFUNDED, refund_time, self.id)
            db.execute('commit;')
        else:
            trades = self.trades
            activity = Activity.get(self.activity_id)
            discount = float(activity.discount)
            try:
                for trade in trades:
                    sql = 'update {table} set status=%s, refund_time=%s where id=%s'.format(table=self.table)
                    db.execute(sql, STATUS_REFUNDED, refund_time, trade.id)

                sql = 'update {table} set status=%s, refund_time=%s where id=%s'.format(table=self.table)
                db.execute(sql, STATUS_REFUNDED, refund_time, self.id)
                # 从活动基金把钱扣除
                sql = 'update {table} set balance=balance-%s where activity_id=%s'.format(talbe=ActivityAccount.table)
                db.execute(sql, amount+discount, self.activity_id)
                # 把钱补回房基金
                if discount:
                    sql = 'update {table} set balance=balance+%s where room_id=%s'.format(table=StarFund.table)
                    db.execute(sql, discount, activity.room_id)
                # 把钱补回用户余额
                sql = 'update {table} set balance=balance+%s where user_id=%s'.format(talbe=Account.table)
                db.execute(sql, amount, self.creator_id)
                db.execute('commit;')
            except:
                db.execute('rollback;')
                raise

        ActivityResult.quit(self.activity_id, self.option_id, self.creator_id)


    def jsonify(self):
        data = {
            'id': self.id,
            'creator_id': self.creator_id,
            'activity_id': self.activity_id,
            'option_id': self.option_id,
            'user_address_id': self.user_address_id,
            'amount': float(self.amount),
            'status': self.status,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        trades = Trade.gets_by_order_and_type(self.id, ORDER_ACTIVITY)
        trades_info = []
        for trade in trades:
            trades_info.append(trade.jsonify())

        data['trades_info'] = trades_info
        return data

