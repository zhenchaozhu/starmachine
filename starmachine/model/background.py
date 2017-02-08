# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager

class UserBackground(object):

    table = 'user_background'

    def __init__(self, id=None, user_id=None, short_url=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.short_url = short_url
        self.create_time = create_time
        self.update_time = update_time

    @classmethod
    def add(cls, user_id, short_url):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (user_id, short_url, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, short_url, create_time)

    @classmethod
    def update(cls, user_id, short_url):
        update_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set short_url=%s, update_time=%s where user_id=%s'.format(table=cls.table)
        db.execute(sql, short_url, update_time, user_id)

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
        user_background = db.get(sql, user_id)
        return user_background and cls(**user_background)


class UserRoomBackground(object):

    table = 'user_room_background'

    def __init__(self, id=None, user_id=None, room_id=None, short_url=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.room_id = room_id
        self.short_url = short_url
        self.create_time = create_time
        self.update_time = update_time

    @classmethod
    def add(cls, user_id, room_id, short_url):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (user_id, room_id, short_url, create_time) values (%s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, room_id, short_url, create_time)

    @classmethod
    def update(cls, user_id, room_id, short_url):
        update_time = datetime.now()
        db = DbManager().db
        sql = 'update {table} set short_url=%s, update_time=%s where user_id=%s and room_id=%s'.format(table=cls.table)
        db.execute(sql, short_url, update_time, user_id, room_id)

    @classmethod
    def exists_user_room(cls, user_id, room_id):
        db = DbManager().db
        sql = 'select id from {table} where user_id=%s and room_id=%s'.format(table=cls.table)
        rst = db.get(sql, user_id, room_id)
        return bool(rst)

    @classmethod
    def get_by_user_room(cls, room_id, user_id):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
        rst = db.get(sql, room_id, user_id)
        return rst and cls(**rst)
