# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import WELFARE_ORDER_PENDING, WELFARE_ORDER_DELIVER, WELFARE_ORDER_COMFIRM
from starmachine.model.user import User

class WelfareOrder(object):

    table = 'welfare_order'

    def __init__(self, id=None, user_id=None, welfare_id=None, address_id=None, status=None, create_time=None,
        delivery_time=None, confirm_time=None):
        self.id = id
        self.user_id = user_id
        self.welfare_id = welfare_id
        self.address_id = address_id
        self.status = status
        self.create_time = create_time
        self.delivery_time = delivery_time
        self.confirm_time = confirm_time

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, user_id, welfare_id, address_id, status=WELFARE_ORDER_PENDING):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (user_id, welfare_id, address_id, status, create_time) values (%s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, welfare_id, address_id, status, create_time)

    @classmethod
    def has_robed(cls, welfare_id, user_id):
        db = DbManager().db
        sql = 'select id from {table} where welfare_id=%s and user_id=%s'.format(table=cls.table)
        try:
            return db.query(sql, welfare_id, user_id)[0]
        except:
            return None

    @classmethod
    def get_robers_count(cls, welfare_id):
        db = DbManager().db
        sql = 'select count(id) from {table} where welfare_id=%s'.format(table=cls.table)
        rst = db.get(sql, welfare_id)
        return rst and rst.get('count(id)')

    @classmethod
    def gets_by_welfare(cls, welfare_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where welfare_id=%s order by create_time limit %s, %s'.format(table=cls.table)
        welfare_orders = db.query(sql, welfare_id, start, count)
        return welfare_orders and [cls(**welfare_order) for welfare_order in welfare_orders]

    @classmethod
    def get_list_user_and_welfare(cls, user_id, welfare_id, start=0, count=10):
        db = DbManager().db
        if start == 0:
            data = []
            sql = 'select * from {table} where user_id=%s and welfare_id=%s'.format(table=cls.table)
            user_welfare_order = db.get(sql, user_id, welfare_id)
            if user_welfare_order:
                count = count - 1
                data.append(user_welfare_order)
            sql = 'select * from {table} where welfare_id=%s and user_id != %s order by create_time limit %s, %s'.format(table=cls.table)
            welfare_orders = db.query(sql, welfare_id, user_id, start ,count)
            data.extend(welfare_orders)
        else:
            sql = 'select * from {table} where welfare_id=%s order by create_time limit %s, %s'.format(table=cls.table)
            data = db.query(sql, welfare_id, start, count)

        return data and [cls(**d) for d in data]

    @classmethod
    def get_by_welfare_and_user(cls, welfare_id, user_id):
        db = DbManager().db
        sql = 'select * from {table} where welfare_id=%s and user_id=%s'.format(table=cls.table)
        welfare_order = db.get(sql, welfare_id, user_id)
        return welfare_order and cls(**welfare_order)

    @classmethod
    def gets_delivery_orders(cls):
        db = DbManager().db
        sql = 'select * from {table} where status=%s'.format(table=cls.table)
        welfare_orders = db.query(sql, WELFARE_ORDER_DELIVER)
        return welfare_orders and [cls(**welfare_order) for welfare_order in welfare_orders]

    @classmethod
    def get_robed_users_by_welfare(cls, welfare_id):
        db = DbManager().db
        sql = 'select * from {table} where welfare_id=%s and status=%s'.format(table=cls.table)
        welfare_orders = db.query(sql, welfare_id, WELFARE_ORDER_PENDING)
        return welfare_orders and [User.get(welfare_order.user_id) for welfare_order in welfare_orders]

    def delivery(self):
        db = DbManager().db
        now = datetime.now()
        sql = 'update {table} set status=%s, delivery_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, WELFARE_ORDER_DELIVER, now, self.id)

    def confirm(self):
        db = DbManager().db
        now = datetime.now()
        sql = 'update {table} set status=%s, confirm_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, WELFARE_ORDER_COMFIRM, now, self.id)
