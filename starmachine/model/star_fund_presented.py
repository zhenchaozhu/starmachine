# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import STAR_FUND_RANK_SEND
from starmachine.model.star_fund_record import StarFundRecord

class StarFundPresented(object):

    table = 'star_fund_presented'

    def __init__(self, id=None, room_id=None, amount=None, intro=None, create_time=None):
        self.id = id
        self.room_id = room_id
        self.amount = amount
        self.intro = intro
        self.create_time = create_time

    @classmethod
    def add(cls, room_id, amount, intro):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (room_id, amount, intro, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        presented_id = db.execute(sql, room_id, amount, intro, create_time)
        sql = 'insert into {table} (room_id, source, amount, create_time, extra, extra_info) values (%s, %s, %s, %s, %s, %s)'.\
            format(table=StarFundRecord.table)
        db.execute(sql, room_id, STAR_FUND_RANK_SEND, amount, create_time, presented_id, intro)

