# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.user import User

class Advice(object):

    table = 'advice'

    def __init__(self, id=None, creator_id=None, reply_user_id=None, text=None, create_time=None):
        self.id = id
        self.creator_id = creator_id
        self.reply_user_id = reply_user_id
        self.text = text
        self.create_time = create_time

    @property
    def creator(self):
        if self.creator_id:
            return User.get(self.creator_id)

    @classmethod
    def add(cls, creator_id, reply_user_id, text):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (creator_id, reply_user_id, text, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, creator_id, reply_user_id, text, create_time)

    @classmethod
    def get_advices_by_user(cls, user_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where (user_id=%s or reply_user_id=%s) order by create_time desc limit %s, %s'.format(table=cls.table)
        advices = db.query(sql, user_id, start, count)
        return advices and [cls(**advice) for advice in advices]

    @classmethod
    def get_advices(cls, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} order by create_time desc limit %s, %s'.format(table=cls.table)
        advices = db.query(sql, start, count)
        return advices and [cls(**advice) for advice in advices]

    def jsonify(self):
        data = {
            'id': self.id,
            'text': self.text,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if self.creator_id:
            creator = User.get(self.creator_id)
            data.update({
                'creator': {
                    'id': creator.id,
                    'name': creator.user_name,
                    'avatar': creator.avatar_url,
                }
            })