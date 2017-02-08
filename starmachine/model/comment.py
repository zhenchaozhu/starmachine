# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.user import User
from starmachine.lib.utils import redis_cache_obj
from starmachine.model.consts import CONTENT_COMMENT_CACHE_KEY
from starmachine.model.content import Content

COMMENT_CACHE_KEY = 'comment:%s'

class Comment(object):

    table = 'comment'

    def __init__(self, id=None, user_id=None, reply_user_id=None, content_id=None, text=None, create_time=None):
        self.id = id
        self.user_id = user_id
        self.reply_user_id = reply_user_id
        self.content_id = content_id
        self.text = text
        self.create_time = create_time

    def __repr__(self):
        return '<Comment:id=%s>' % (self.id)

    @property
    def creator(self):
        return User.get(self.user_id)

    @property
    def content(self):
        return Content.get(self.content_id)

    @classmethod
    @redis_cache_obj(COMMENT_CACHE_KEY)
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        comment_info = db.get(sql, id)
        return comment_info and cls(**comment_info)

    @classmethod
    def add(cls, user_id, reply_user_id, content_id, text):
        db = DbManager().db
        create_time = datetime.now()
        cache = CacheManager().cache
        cache_key = CONTENT_COMMENT_CACHE_KEY % content_id
        sql = 'insert into {table} (user_id, reply_user_id, content_id, text, create_time) values ' \
            '(%s, %s, %s, %s, %s)'.format(table=cls.table)
        comment_id = db.execute(sql, user_id, reply_user_id, content_id, text, create_time)
        if comment_id:
            content = Content.get(content_id)
            content.update(last_comment_time=create_time)
            cache.lpush(cache_key, comment_id)
            return cls(comment_id, user_id, reply_user_id, content_id, text, create_time)

    @classmethod
    def get_comments_by_content(cls, content_id, start, count):
        cache = CacheManager().cache
        cache_key = CONTENT_COMMENT_CACHE_KEY % content_id
        end = start + count - 1
        comment_ids = cache.lrange(cache_key, start, end)
        comments = [cls.get(comment_id) for comment_id in comment_ids]
        return comments

    @classmethod
    def get_comment_by_content_and_creator(cls, content_id, creator_id):
        db = DbManager().db
        sql = 'select * from comment where content_id=%s and user_id=%s'
        rst = db.query(sql, content_id, creator_id)
        return rst and rst[0]

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        comments = db.query(sql)
        return comments and [cls(**comment) for comment in comments]

    def delete(self):
        db = DbManager().db
        sql = 'delete from {table} where id=%s'.format(table=self.table)
        db.execute(sql, self.id)
        self.flush_comment_cache()

    def flush_comment_cache(self):
        cache = CacheManager().cache
        cache_obj_key = COMMENT_CACHE_KEY % self.id
        cache_list_key = CONTENT_COMMENT_CACHE_KEY % self.content_id
        cache.delete(cache_obj_key)
        cache.lrem(cache_list_key, 0, self.id)

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        db.execute(sql)


    def jsonify(self):
        data = {
            'id': self.id,
            'user': {
                'id': self.creator.id,
                'name': self.creator.user_name,
                'avatar': self.creator.avatar_url,
            },
            'user_id': self.user_id,
            'content_id': self.content_id,
            'text': self.text,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                            self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        reply_user = User.get(self.reply_user_id)
        if reply_user:
            data.update({
                'reply': {
                    'id': reply_user.id,
                    'name': reply_user.user_name,
                    'avatar': reply_user.avatar_url,
                }
            })

        return data