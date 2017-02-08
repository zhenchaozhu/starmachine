# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.user import User
from starmachine.model.room import Room
from starmachine.model.content import Content
from starmachine.model.consts import VOTE_TYPE, CONTENT_REWARD_AMOUNT_CACHE_KEY, CONTENT_LIKED_RANK_KEY, \
    CONTENT_COMMENT_CACHE_KEY, CONTENT_REWARD_CACHE_KEY, VOTE_OPTION_PEOPLE_CACHE_KEY, VOTE_PEOPLE_CACHE_KEY, \
    USER_CREATED_CONTENT_KEY, CONTENT_PUBLIC, USER_DAILY_VOTE_COUNT
from starmachine.lib.utils import get_int_date, init_pic_url
from starmachine.model.room_user import RoomUser

class Vote(object):

    table = 'vote'

    def __init__(self, id=None, creator_id=None, room_id=None, name=None, deadline=None, create_time=None, update_time=None):
        self.id = id
        self.creator_id = creator_id
        self.room_id = room_id
        self.name = name
        self.deadline = deadline
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Vote:id=%s>' % (self.id)

    @property
    def creator(self):
        return User.get(self.creator_id)

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

    @property
    def voted_amount(self):
        return VoteResult.get_voted_amounts(self.id)

    @property
    def expired(self):
        now = datetime.now()
        if isinstance(self.deadline, datetime):
            return self.deadline < now
        else:
            return self.deadline < now.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def add(cls, creator_id, room_id, name, deadline, options, room_user_status, status=CONTENT_PUBLIC):
        room = Room.get(room_id)
        db = DbManager().db
        create_time = datetime.now()
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, room_id, content_type, status, create_time, last_comment_time, room_user_status) values ' \
                  '(%s, %s, %s, %s, %s, %s, %s)'.format(table=Content.table)
            content_id = db.execute(sql, creator_id, room_id, VOTE_TYPE, status, create_time, create_time, room_user_status)
            sql = 'insert into {table} (id, creator_id, room_id, name, deadline, create_time) values ' \
                '(%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            db.execute(sql, content_id, creator_id, room_id, name, deadline, create_time)
            for option in options:
                sql = 'insert into {table} (vote_id, content, create_time) values (%s, %s, %s)'.format(table=VoteOption.table)
                db.execute(sql, content_id, option, create_time)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        cls.save_created_content_to_redis(creator_id, content_id, create_time)
        room.update(last_content_updated=create_time, update_time=create_time)
        return content_id and cls.get(content_id)

    @classmethod
    def save_created_content_to_redis(cls, creator_id, content_id, create_time):
        cache = CacheManager().cache
        score = get_int_date(create_time)
        cache_content_key = USER_CREATED_CONTENT_KEY % creator_id
        cache.zadd(cache_content_key, score, content_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        vote_info = db.get(sql, id)
        return vote_info and cls(**vote_info)

    def delete(self):
        db = DbManager().db
        vote_id = self.id
        db.execute('begin;')
        try:
            sql = 'delete from {table} where id=%s'.format(table=self.table)
            db.execute(sql, vote_id)
            sql = 'delete from {table} where vote_id=%s'.format(table=VoteOption.table)
            db.execute(sql, vote_id)
            sql = 'delete from {table} where vote_id=%s'.format(table=VoteResult.table)
            db.execute(sql, vote_id)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

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
        options = VoteOption.gets_option_by_vote(self.id)
        data = {
            'id': self.id,
            'creator': {
                'id': self.creator.id,
                'name': self.creator.user_name,
                'avatar': self.creator.avatar_url,
            },
            'name': self.name,
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                        self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'options': [option.jsonify() for option in options],
            'content_type': VOTE_TYPE,
            'reward_amount': self.reward_amount,
            'like_amount': self.like_amount,
            'comment_amount': self.comment_amount,
            'reward_user_amount': self.reward_user_amount,
            'voted_amount': self.voted_amount,
            'expired': self.expired,
            'robed_user_amount': 0,
        }

        if user:
            data.update({
                'has_liked': bool(ContentLiked.has_liked(self.id, user.id)),
                'has_voted': bool(VoteResult.has_voted(self.id, user.id)),
                'has_robed': False,
                'has_delivery': False,
            })
            room_user = RoomUser.get_by_room_and_user(self.room_id, user.id)
            if room_user:
                data.update({
                    'room_user_status': room_user.status,
                })

        return data


class VoteOption(object):

    table = 'vote_option'

    def __init__(self, id, vote_id, content, create_time, update_time):
        self.id = id
        self.vote_id = vote_id
        self.content = content
        self.create_time = create_time
        self.update_time = update_time

    @property
    def voted_amounts(self):
        return VoteResult.get_voted_amounts_by_option(self.id)

    @classmethod
    def add(cls, vote_id, content):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (vote_id, content, create_time) values (%s, %s, %s)'.format(table=cls.table)
        option_id = db.execute(sql, vote_id, content, create_time)
        return option_id and cls.get(option_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        option_info = db.get(sql, id)
        return option_info and cls(**option_info)

    @classmethod
    def gets_option_by_vote(cls, vote_id):
        db = DbManager().db
        sql = 'select * from {table} where vote_id=%s'.format(table=cls.table)
        options = db.query(sql, vote_id)
        return options and [cls(**option) for option in options]

    def jsonify(self):
        return {
            'id': self.id,
            'content': self.content,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                        self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'voted_amounts': self.voted_amounts,
        }


class VoteResult(object):

    table = 'vote_result'

    def __init__(self, id, user_id, vote_id, option_id, create_time, update_time):
        self.id = id
        self.user_id = user_id
        self.vote_id = vote_id
        self.option_id = option_id
        self.create_time = create_time
        self.update_time = update_time

    @property
    def user(self):
        return User.get(self.user_id)

    @property
    def vote(self):
        return Vote.get(self.vote_id)

    @property
    def option(self):
        return VoteOption.get(self.option_id)

    @classmethod
    def add(cls, user_id, vote_id, option_id):
        db = DbManager().db
        cache = CacheManager().cache
        create_time = datetime.now()
        date = create_time.date()
        vote_cache_key = VOTE_PEOPLE_CACHE_KEY % vote_id
        option_cache_key = VOTE_OPTION_PEOPLE_CACHE_KEY % option_id
        vote_daily_count_redis_key = USER_DAILY_VOTE_COUNT % (user_id, date)
        sql = 'insert into {table} (user_id, vote_id, option_id, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, vote_id, option_id, create_time)
        cache.zadd(vote_cache_key, get_int_date(create_time), user_id)
        cache.zadd(option_cache_key, get_int_date(create_time), user_id)
        cache.incr(vote_daily_count_redis_key, 1)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        vote_result = db.get(sql, id)
        return vote_result and cls(**vote_result)

    @classmethod
    def get_voted_amounts_by_option(cls, option_id):
        cache = CacheManager().cache
        cache_key = VOTE_OPTION_PEOPLE_CACHE_KEY % option_id
        return cache.zcard(cache_key)

    @classmethod
    def get_voted_amounts(cls, vote_id):
        cache = CacheManager().cache
        cache_key = VOTE_PEOPLE_CACHE_KEY % vote_id
        return cache.zcard(cache_key)

    @classmethod
    def has_voted(cls, vote_id, user_id):
        cache = CacheManager().cache
        key = VOTE_PEOPLE_CACHE_KEY % vote_id
        return cache.zscore(key, user_id)

    def jsonify(self):
        return {
            'id': self.id,
            'user': self.user.jsonify(),
            'option': self.option.jsonify()
        }