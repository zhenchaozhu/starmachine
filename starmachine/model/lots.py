# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager

class Lots(object):

    table = 'lots'

    def __init__(self, id=None, content=None, create_time=None):
        self.id = id
        self.content = content
        self.create_time = create_time

    @classmethod
    def add(cls, content):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (content, create_time) values (%s, %s)'.format(table=cls.table)
        db.execute(sql, content, create_time)

    @classmethod
    def get_random_lots(cls):
        db = DbManager().db
        sql = 'select * from {table} as t1 join(select round(rand() * ((select max(id) from {table}) - ' \
              '(select min(id) from {table})) + (select min(id) from {table})) as id) as t2 where ' \
              't1.id >= t2.id ORDER BY t1.id LIMIT 1'.format(table=cls.table)
        rst = db.get(sql)
        return rst and cls(**rst)

    def jsonify(self):
        return {
            'id': self.id,
            'content': self.content,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }


class DrawLots(object):

    table = 'draw_lots'

    def __init__(self, id=None, user_id=None, lots_id=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.lots_id = lots_id
        self.create_time = create_time

    @classmethod
    def add(cls, user_id, lots_id):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (user_id, lots_id, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, lots_id, create_time)
