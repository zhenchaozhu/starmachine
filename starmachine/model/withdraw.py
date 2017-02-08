# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import WITHDRAW_WAITING, WITHDRAW_PENDING, WITHDRAW_COMPLETE, WITHDRAW_FAIL
from starmachine.model.account import Account

ALIPAY_ACCOUNT_TYPE = 1

class WithdrawAccount(object):

    table = 'withdraw_account'

    def __init__(self, id=None, user_id=None, name=None, account_type=None, account_name=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.account_type = account_type
        self.account_name = account_name
        self.create_time = create_time

    def __repr__(self):
        return '<WithdrawAccount:id=%s>' % (self.id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def gets_by_user(cls, user_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s order by create_time desc limit %s, %s'.format(table=cls.table)
        accounts = db.query(sql, user_id, start, count)
        return accounts and [cls(**account) for account in accounts]

    @classmethod
    def add(cls, user_id, name, account_name, account_type=ALIPAY_ACCOUNT_TYPE):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, name, account_type, account_name, create_time) values (%s, %s, %s, %s, %s)'.format(table=cls.table)
        account_id = db.execute(sql, user_id, name, account_type, account_name, create_time)
        if account_id:
            return cls(account_id, user_id, name, account_type, account_name, create_time)

    def jsonify(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_type': self.account_type,
            'account_name': self.account_name,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }


class Withdraw(object):

    table = 'withdraw'

    def __init__(self, id=None, user_id=None, withdraw_account=None, amount=None, status=None, create_time=None,
        pending_time=None, withdraw_time=None, extra=None):
        self.id = id
        self.user_id = user_id
        self.withdraw_account = withdraw_account
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.pending_time = pending_time
        self.withdraw_time = withdraw_time
        self.extra = extra

    def __repr__(self):
        return '<Withdraw:id=%s>' % (self.id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, user_id, withdraw_account, amount, status=WITHDRAW_WAITING):
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (user_id, withdraw_account, amount, status, create_time) values ' \
            '(%s, %s, %s, %s, %s)'.format(table=cls.table)
            db.execute(sql, user_id, withdraw_account, amount, status, create_time)
            sql = 'update {table} set balance=balance-%s where user_id=%s'.format(table=Account.table)
            db.execute(sql, amount, user_id)
            db.execute('commit;')
        except Exception as e:
            db.execute('rollback;')
            raise

    @classmethod
    def get_lists(cls, start, count):
        db = DbManager().db
        end = start * count - 1
        sql = 'select * from {table} order by id desc limit %s, %s'.format(table=cls.table)
        withdraws = db.query(sql, start, end)
        return withdraws and [cls(**withdraw) for withdraw in withdraws]

    @classmethod
    def get_amount(cls):
        db = DbManager().db
        sql = 'select count(id) from {table}'.format(table=cls.table)
        count = db.get(sql)
        return count and count.get('count(id)')

    def pending(self):
        pending_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set status=%s, pending_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, WITHDRAW_PENDING, pending_time, self.id)

    def complete(self, info):
        withdraw_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set status=%s, withdraw_time=%s, extra_info=%s where id=%s'.format(table=self.table)
        db.execute(sql, WITHDRAW_COMPLETE, withdraw_time, info, self.id)

    def fail(self, info):
        withdraw_time = datetime.now()
        db = DbManager().db
        db.execute('begin;')
        try:
            sql = 'update {table} set status=%s, withdraw_time=%s, extra_info=%s where id=%s'.format(table=self.table)
            db.execute(sql, WITHDRAW_FAIL, withdraw_time, info, self.id)
            sql = 'update {table} set balance=balance+%s where user_id=%s'.format(table=Account.table)
            db.execute(sql, self.amount, self.user_id)
            db.execute('commit;')
        except Exception as e:
            db.execute('rollback;')
            raise

class WithdrawBatch(object):

    table = 'withdraw_batch'

    def __init__(self, id=None, batch_no=None, withdraw_ids=None, success_details=None, fail_details=None, status=None,
        create_time=None):
        self.id = id
        self.batch_no = batch_no
        self.withdraw_ids = withdraw_ids
        self.success_details = success_details
        self.fail_details = fail_details
        self.status = status
        self.create_time = create_time

    @classmethod
    def add(cls, batch_no, withdraw_ids, create_time):
        db = DbManager().db
        sql = 'insert into {table} (batch_no, withdraw_ids, status, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, batch_no, withdraw_ids, 'P', create_time)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    def handle_trans(self, success_details, fail_details):
        success_details = success_details.split('|')
        fail_details = fail_details.split('|')
        if success_details:
            for d in success_details:
                detail = d.split('^')
                withdraw_id = detail[0]
                success_info = detail[5]
                withdraw = Withdraw.get(withdraw_id)
                if withdraw:
                    withdraw.complete(success_info)

        if fail_details:
            for d in fail_details:
                detail = d.split('^')
                withdraw_id = detail[0]
                fail_info = detail[5]
                withdraw = Withdraw.get(withdraw_id)
                if withdraw:
                    withdraw.fail(fail_info)



