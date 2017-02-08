# coding: utf-8

import time
from datetime import datetime
import json
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.user import User
from starmachine.lib.utils import redis_cache_obj, get_int_date, init_pic_url
from starmachine.model.consts import CONTENT_PUBLIC, POSTS_TYPE, CONTENT_REWARD_AMOUNT_CACHE_KEY, CONTENT_LIKED_RANK_KEY, \
    CONTENT_COMMENT_CACHE_KEY, CONTENT_REWARD_CACHE_KEY, CONTENT_LIKED_CACHE_KEY, USER_CREATED_CONTENT_KEY, \
    COMMENT_CACHE_KEY, CONTENT_COMMENT_CACHE_KEY, POSTS_CACHE_KEY
from starmachine.model.content import Content
from starmachine.model.user import User
from starmachine.model.room import Room
from starmachine.model.room_user import RoomUser
from starmachine.model.content.content_like import ContentLiked

class Posts(object):

    table = 'posts'

    def __init__(self, id=None, creator_id=None, room_id=None, text=None, images=None, video=None, create_time=None, update_time=None):
        self.id = id
        self.creator_id = creator_id
        self.room_id = room_id
        self.text = text
        self.images = images
        self.video = video
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Posts:id=%s>' % (self.id)

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def room(self):
        return Room.get(self.room_id)

    @property
    def reward_amount(self):
        cache = CacheManager().cache
        reward_amount = cache.zscore(CONTENT_REWARD_AMOUNT_CACHE_KEY, self.id)
        return reward_amount if reward_amount else 0

    @property
    def like_amount(self):
        cache = CacheManager().cache
        like_amount = cache.zscore(CONTENT_LIKED_RANK_KEY, self.id)
        return like_amount if like_amount else 0

    @property
    def comment_amount(self):
        cache = CacheManager().cache
        cache_key = CONTENT_COMMENT_CACHE_KEY % self.id
        return cache.llen(cache_key)

    @property
    def reward_user_amount(self):
        cache = CacheManager().cache
        cache_key = CONTENT_REWARD_CACHE_KEY % self.id
        return cache.llen(cache_key)

    @classmethod
    def add(cls, creator_id, room_id, text, images, video, room_user_status, status=CONTENT_PUBLIC):
        room = Room.get(room_id)
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, room_id, content_type, status, create_time, last_comment_time, room_user_status) values' \
                  ' (%s, %s, %s, %s, %s, %s, %s)'.format(table=Content.table)
            content_id = db.execute(sql, creator_id, room_id, POSTS_TYPE, status, create_time, create_time, room_user_status)
            sql = 'insert into {table} (id, creator_id, room_id, text, images, video, create_time) values ' \
                '(%s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            db.execute(sql, content_id, creator_id, room_id, text, images, video, create_time)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        room.update(last_content_updated=create_time, update_time=create_time)
        cls.save_created_content_to_redis(creator_id, content_id, create_time)
        return content_id and cls.get(content_id)

    @classmethod
    def save_created_content_to_redis(cls, creator_id, content_id, create_time):
        cache = CacheManager().cache
        score = get_int_date(create_time)
        cache_content_key = USER_CREATED_CONTENT_KEY % creator_id
        cache.zadd(cache_content_key, score, content_id)

    @classmethod
    @redis_cache_obj(POSTS_CACHE_KEY)
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        text_info = db.get(sql, id)
        return text_info and cls(**text_info)

    def delete(self):
        db = DbManager().db
        content_id = self.id
        db.execute('begin;')
        try:
            sql = 'delete from {table} where id=%s'.format(table=self.table)
            db.execute(sql, content_id)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        cache = CacheManager().cache
        posts_cache_key = POSTS_CACHE_KEY % content_id
        cache.delete(posts_cache_key)

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
        from starmachine.model.content.content_like import ContentLiked
        from starmachine.model.content.vote import VoteResult
        data = {
            'id': self.id,
            'creator': {
                'id': self.creator.id,
                'name': self.creator.user_name,
                'avatar': self.creator.avatar_url,
            },
            'text': self.text if self.text else None,
            'video': self.video if self.video else None,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'content_type': POSTS_TYPE,
            'reward_amount': self.reward_amount,
            'like_amount': self.like_amount,
            'comment_amount': self.comment_amount,
            'reward_user_amount': self.reward_user_amount,
            'robed_user_amount': 0,
        }

        if self.images:
            image_urls = []
            images = json.loads(self.images)
            for image in images:
                image_url = init_pic_url(image)
                image_urls.append(image_url)

            data['images'] = image_urls
        else:
            data['images'] = []
        if user:
            data.update({
                'has_liked': bool(ContentLiked.has_liked(self.id, user.id)),
                'has_robed': False,
                'has_delivery': False,
            })

        return data

