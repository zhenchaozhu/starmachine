# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.consts import POSTS_TYPE, VOTE_TYPE, CONTENT_PUBLIC, WELFARE_TYPE, USER_CREATED_CONTENT_KEY, \
    POSTS_CACHE_KEY, CONTENT_COMMENT_CACHE_KEY, COMMENT_CACHE_KEY, CONTENT_LIKED_CACHE_KEY, CONTENT_LIKED_RANK_KEY
from starmachine.model.user import User
from starmachine.model.room import Room

def getContentTypeMap():
    from starmachine.model.content.posts import Posts
    from starmachine.model.content.vote import Vote
    from starmachine.model.content.welfare import Welfare

    return {
        POSTS_TYPE: Posts,
        VOTE_TYPE: Vote,
        WELFARE_TYPE: Welfare,
    }

class Content(object):

    table = 'content'

    def __init__(self, id=None, creator_id=None, room_id=None, content_type=None, status=None, create_time=None,
        update_time=None, last_comment_time=None, room_user_status=None):
        self.id = id
        self.creator_id = creator_id
        self.room_id = room_id
        self.content_type = content_type
        self.status = status # 公开还是隐藏
        self.create_time = create_time
        self.update_time = update_time
        self.last_comment_time = last_comment_time
        self.room_user_status = room_user_status # 内容创建者在房间中的身份

    def __repr__(self):
        return '<Content:id=%s>' % (self.id)

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def room(self):
        return Room.get(self.room_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        content_info = db.get(sql, id)
        return content_info and cls(**content_info)

    @classmethod
    def gets_by_room(cls, room_id, user_id, start, count):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s and (creator_id=%s or status=%s) order by last_comment_time ' \
            'desc limit %s, %s'.format(table=cls.table)
        room_contents = db.query(sql, room_id, user_id, CONTENT_PUBLIC, start, count)
        return room_contents and [cls(**room_content) for room_content in room_contents]

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        contents = db.query(sql)
        return [cls(**content) for content in contents]

    @classmethod
    def get_contents_by_user(cls, user_id, start, count):
        cache = CacheManager().cache
        end = start + count - 1
        content_ids = cache.zrevrange(USER_CREATED_CONTENT_KEY % user_id, start, end)
        return content_ids and [Content.get(content_id) for content_id in content_ids]

    def delete(self):
        db = DbManager().db
        content_id = self.id
        db.execute('begin;')
        try:
            sql = 'delete from {table} where id=%s'.format(table=self.table)
            db.execute(sql, content_id)
            sql = 'delete from comment where content_id=%s'
            db.execute(sql, content_id)
            sql = 'delete from content_liked where content_id=%s'
            db.execute(sql, content_id)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        cache = CacheManager().cache
        cache.zrem(USER_CREATED_CONTENT_KEY % self.creator_id, content_id)
        # 删除内容的评论和点赞记录
        content_comment_key = CONTENT_COMMENT_CACHE_KEY % content_id
        comment_ids = cache.lrange(content_comment_key, 0, -1)
        with cache.pipeline() as pipe:
            for comment_id in comment_ids:
                comment_cache_key = COMMENT_CACHE_KEY % comment_id
                pipe.delete(comment_cache_key)

            pipe.delete(content_comment_key)
            content_liked_key = CONTENT_LIKED_CACHE_KEY % content_id
            pipe.delete(content_liked_key)
            pipe.zrem(CONTENT_LIKED_RANK_KEY, content_id)
            pipe.execute()

        ContentTypeMap = getContentTypeMap()
        content_model = ContentTypeMap.get(self.content_type)
        content_obj = content_model.get(self.id)
        content_obj.delete()

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        r = db.execute(sql)
        return r

    def jsonify(self, user=None):
        ContentTypeMap = getContentTypeMap()
        content_model = ContentTypeMap.get(self.content_type)
        content_obj = content_model.get(self.id)
        return content_obj.jsonify(user)