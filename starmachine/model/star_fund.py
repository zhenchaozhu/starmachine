# coding: utf-8

from starmachine.lib.query import DbManager
from starmachine.lib.utils import redis_cache_obj

STAR_FUND_CACHE_KEY = 'star_fund:%s'

class StarFund(object):

    table = 'star_fund'

    def __init__(self, id=None, room_id=None, balance=None):
        self.id = id
        self.room_id = room_id
        self.balance = balance

    def __repr__(self):
        return '<StarFund:id=%s>' % (self.id)

    @classmethod
    def add(cls, room_id, balance):
        db = DbManager().db
        sql = 'insert into {table} (room_id, balance) values (%s, %s)'.format(table=cls.table)
        star_fund_id = db.execute(sql, room_id, balance)
        if star_fund_id:
            return cls.get(star_fund_id)

    @classmethod
    @redis_cache_obj(STAR_FUND_CACHE_KEY)
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        star_fund_info = db.get(sql, id)
        return star_fund_info and cls(**star_fund_info)

    @classmethod
    def get_by_room(cls, room_id):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s'.format(table=cls.table)
        star_fund_info = db.get(sql, room_id)
        return star_fund_info and cls(**star_fund_info)

    def jsonify(self):
        return {
            'id': id,
            'room_id': self.room_id,
            'balance': float(self.balance),
        }

