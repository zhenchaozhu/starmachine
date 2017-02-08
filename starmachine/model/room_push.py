# coding: utf-8

from datetime import datetime, timedelta
from starmachine.lib.query import DbManager
from starmachine.model.consts import ROOM_PUSH_FAIL, ROOM_PUSH_PENDING, ROOM_PUSH_COMPLETE

class RoomPush(object):

    table = 'room_push'
    def __init__(self, id=None, user_id=None, room_id=None, content_id=None, push_time=None, status=None):
        self.id = id
        self.user_id = user_id
        self.room_id = room_id
        self.content_id = content_id
        self.push_time = push_time
        self.status = status

    @classmethod
    def add(cls, user_id, room_id, content_id, status=ROOM_PUSH_PENDING):
        push_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (user_id, room_id, content_id, push_time, status) values (%s, %s, %s, %s, %s)'.format(table=cls.table)
        room_push_id = db.execute(sql, user_id, room_id, content_id, push_time, status)
        return cls(room_push_id, user_id, room_id, content_id, push_time, status)

    @classmethod
    def get_push_count_by_room_and_date(cls, room_id, date):
        db = DbManager().db
        date = date.date()
        start = date.strftime('%Y-%m-%d')
        end = (date + timedelta(days=1)).strftime('%Y-%m-%d')
        sql = 'select count(id) from {table} where room_id=%s and %s < push_time and push_time < %s and status!=%s'.format(table=cls.table)
        rst = db.get(sql, room_id, start, end, ROOM_PUSH_FAIL)
        return rst and rst.get('count(id)')

    def complete(self):
        db = DbManager().db
        sql = 'update {table} set status=%s where id=%s'.format(table=self.table)
        db.execute(sql, ROOM_PUSH_COMPLETE, self.id)

    def fail(self):
        db = DbManager().db
        sql = 'update {table} set status=%s where id=%s'.format(table=self.table)
        db.execute(sql, ROOM_PUSH_FAIL, self.id)