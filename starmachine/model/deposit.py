# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import STATUS_PENDING, STATUS_COMPLETE

class Deposit(object):

    table = 'deposit'

    def __init__(self, id, account_name, account_type, amount, status, create_time, deposit_time):
        self.id = id
        self.account_name = account_name
        self.account_type = account_type
        self.amount = amount
        self.status = status
        self.create_time = create_time
        self.deposit_time = deposit_time

    def __repr__(self):
        return '<Deposit:id=%s>' % (self.id)

    @classmethod
    def add(cls, account_name, account_type, amount, status=STATUS_PENDING):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (account_name, account_type, amount, status, create_time)'.format(table=cls.table)
        db.execute(sql, account_name, account_type, amount, status, create_time)

    def complete(self):
        deposit_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set status=%s, deposit_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, STATUS_COMPLETE, deposit_time, self.id)

