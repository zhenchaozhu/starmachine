# coding: utf-8

from datetime import datetime, timedelta
from starmachine.lib.query import DbManager
from starmachine.model.consts import USER_INTEGRAL_DAILY_LOGIN, USER_INTEGRAL_DAILY_CREATE_CONTENT, USER_INTEGRAL_DAILY_DRAW_LOTS, \
    USER_INTEGRAL_DAILY_COMMENT, USER_INTEGRAL_DAILY_VOTE, USER_INTEGRAL_DAILY_GET_LIKED, USER_INTEGRAL_DAILY_GET_REWARD, \
    USER_INTEGRAL_DAILY_SEND_REWARD, USER_INTEGRAL_DAILY_CREATE_WELFARE, USER_INTEGRAL_DAILY_ROB_WELFARE


class UserIntegral(object):

    table = 'user_integral'

    def __init__(self, id=None, user_id=None, integral=None):
        self.id = id
        self.user_id = user_id
        self.integral = integral

    @classmethod
    def add(cls, user_id, integral):
        db = DbManager().db
        sql = 'insert into {table} (user_id, integral) values (%s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, integral)

    @classmethod
    def exists_user(cls, user_id):
        db = DbManager().db
        sql = 'select id from {table} where user_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        return bool(rst)

    @classmethod
    def get_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id)
        return rst and cls(**rst)

    def jsonify(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'integral': self.integral,
        }

class UserIntegralRecord(object):

    table = 'user_integral_record'

    def __init__(self, id=None, user_id=None, source=None, amount=None, integral=None, create_date=None, create_time=None, extra=None):
        self.id = id
        self.user_id = user_id
        self.source = source
        self.amount = amount
        self.integral = integral
        self.create_date = create_date
        self.create_time = create_time
        self.extra = extra

    @classmethod
    def add(cls, user_id, source, amount, integral, extra=None):
        db = DbManager().db
        now = datetime.now()
        date = now.date()
        sql = 'insert into {table} (user_id, source, amount, integral, create_date, create_time, extra) values ' \
        '(%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, source, amount, integral, date, now, extra)

    @classmethod
    def has_get_first_reward_integral(cls, user_id, source):
        db = DbManager().db
        sql = 'select id from {table} where user_id=%s and source=%s'.format(table=cls.table)
        try:
            return db.query(sql, user_id, source)[0]
        except:
            return None

    @classmethod
    def daily_login_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.get(sql, user_id, USER_INTEGRAL_DAILY_LOGIN, date)
        return bool(rst)

    @classmethod
    def daily_create_content_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_CREATE_CONTENT, date)
        return len(rst) >= 3

    @classmethod
    def daily_draw_lots_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_DRAW_LOTS, date)
        return len(rst) >= 1

    @classmethod
    def daily_comment_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_COMMENT, date)
        return len(rst) >= 10

    @classmethod
    def daily_vote_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_VOTE, date)
        return len(rst) >= 3

    @classmethod
    def daily_get_liked_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_GET_LIKED, date)
        return len(rst) >= 20

    @classmethod
    def daily_get_reward_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_GET_REWARD, date)
        return len(rst) >= 15

    @classmethod
    def daily_send_reward_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_SEND_REWARD, date)
        return len(rst) >= 10

    @classmethod
    def daily_create_welfare_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now().date()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_CREATE_WELFARE, date)
        return len(rst) >= 3

    @classmethod
    def daily_rob_welfare_integral_enough(cls, user_id):
        db = DbManager().db
        date = datetime.now()
        sql = 'select id from {table} where user_id=%s and source=%s and create_date=%s'.format(table=cls.table)
        rst = db.query(sql, user_id, USER_INTEGRAL_DAILY_ROB_WELFARE, date)
        return len(rst) >= 3

    def jsonify(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source': self.source,
            'amount': float(self.amount),
            'integral': float(self.integral),
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'extra': self.extra
        }