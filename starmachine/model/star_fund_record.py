# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager

class StarFundRecord(object):

    table = 'star_fund_record'

    def __init__(self, id=None, room_id=None, source=None, amount=None, create_time=None, extra=None, extra_info=None):
        self.id = id
        self.room_id = room_id
        self.source = source
        self.amount = amount
        self.create_time = create_time
        self.extra = extra
        self.extra_info = extra_info

    @classmethod
    def add(cls, room_id, source, amount, create_time, extra, extra_info):
        db = DbManager().db
        sql = 'insert into {table} (room_id, source, amount, create_time, extra, extra_info) values ' \
            '(%s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, room_id, source, amount, create_time, extra, extra_info)

    @classmethod
    def gets_by_room(cls, room_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s order by create_time desc limit %s, %s'.format(table=cls.table)
        records = db.query(sql, room_id, start, count)
        return records and [cls(**record) for record in records]

    def jsonify(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'source': self.source,
            'amount': float(self.amount),
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'extra': self.extra,
            'extra_info': self.extra_info,
        }

