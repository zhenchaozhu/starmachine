# coding: utf-8

import random
from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.user import User
from starmachine.model.star_fund import StarFund
from starmachine.lib.utils import redis_cache_obj, init_pic_url
from starmachine.model.consts import ROOM_PUBLIC, USER_CREATED_ROOM_KEY, ROOM_USER_COUNT_KEY, ROOM_USER_CACHE_KEY, \
    ROOM_PRIVATE_NOT_JOIN, ROOM_PRIVATE_NEED_VERIFY, ROOM_USER_REWARD_CACHE_KEY, ROOM_INCREASE_RANK_CACHE_KEY, ROOM_USER_CREATOR
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.tag import Tag

ROOM_CACHE_KEY = 'room:%s'


class Room(object):

    table = 'room'

    def __init__(self, id=None, creator_id=None, name=None, intro=None, avatar=None,
        limit_user_number=None, status=None, create_time=None, update_time=None, last_content_updated=None):
        self.id = id
        self.creator_id = creator_id
        self.name = name
        self.intro = intro
        self.avatar = avatar
        self.limit_user_number = limit_user_number
        self.status = status
        self.create_time = create_time
        self.update_time = update_time
        self.last_content_updated = last_content_updated

    def __repr__(self):
        return '<Room:id=%s>' % (self.id)

    @property
    def public(self):
        return int(self.status) == ROOM_PUBLIC

    @property
    def private_need_verify(self):
        return int(self.status) == ROOM_PRIVATE_NEED_VERIFY

    @property
    def private_not_join(self):
        return int(self.status) == ROOM_PRIVATE_NOT_JOIN

    @property
    def creator(self):
        return User.get(self.creator_id)

    @property
    def user_amount(self):
        cache = CacheManager().cache
        user_count = cache.zscore(ROOM_USER_COUNT_KEY, self.id)
        return user_count if user_count else 0

    @property
    def tags(self):
        from starmachine.model.room_tag import RoomTag
        tag_ids  = RoomTag.get_tag_ids_by_room(self.id)
        return [Tag.get(tag_id) for tag_id in tag_ids if tag_id]

    @property
    def avatar_url(self):
        return init_pic_url(self.avatar)

    @property
    def star_fund(self):
        star_fund = StarFund.get_by_room(self.id)
        return float(star_fund.balance)

    @classmethod
    def add(cls, creator_id, name, intro, tag_ids, avatar, limit_user_number, create_time, status=ROOM_PUBLIC, question_info=None):
        from starmachine.model.room_tag import RoomTag
        from starmachine.model.room_user import RoomUser
        db = DbManager().db
        cache = CacheManager().cache
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, name, intro, avatar, limit_user_number, status, create_time) ' \
                'values (%s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            room_id = db.execute(sql, creator_id, name, intro, avatar, limit_user_number, status, create_time)
            if int(status) == ROOM_PRIVATE_NEED_VERIFY and question_info:
                question_name = question_info.get('question_name')
                options = question_info.get('options')
                sql = 'insert into {table} (room_id, name, create_time) values (%s, %s, %s)'.format(table=RoomQuestion.table)
                room_question_id = db.execute(sql, room_id, question_name, create_time)
                for option in options:
                    text = option.get('text')
                    is_right_answer = option.get('is_right_answer')
                    sql = 'insert into {table} (question_id, text, is_right_answer) values (%s, %s, %s)'.format(table=RoomQuestionOption.table)
                    db.execute(sql, room_question_id, text, is_right_answer)

            for tag_id in tag_ids:
                sql = 'insert into {table} (room_id, tag_id) values (%s, %s)'.format(table=RoomTag.table)
                db.execute(sql, room_id, tag_id)
            sql = 'insert into {table} (room_id, balance) values (%s, %s)'.format(table=StarFund.table)
            db.execute(sql, room_id, '0.00')
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise
        cache_key = USER_CREATED_ROOM_KEY % creator_id
        cache.sadd(cache_key, room_id)
        RoomUser.add(room_id, creator_id, ROOM_USER_CREATOR)
        return room_id

    @classmethod
    @redis_cache_obj(ROOM_CACHE_KEY)
    def get(cls, room_id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        room_info = db.get(sql, room_id)
        return room_info and cls(**room_info)

    @classmethod
    def exist_room(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None

    @classmethod
    def get_rooms_by_user_amount(cls, start=0, count=10):
        cache = CacheManager().cache
        end = start + count - 1
        room_ids = cache.zrevrange(ROOM_USER_COUNT_KEY, start, end)
        return room_ids and [cls.get(room_id) for room_id in room_ids]

    @classmethod
    def get_rooms_increase_rank(cls, year, month, start=0, count=10):
        redis_key = ROOM_INCREASE_RANK_CACHE_KEY % (year, month)
        cache = CacheManager().cache
        end = start + count - 1
        rst = cache.zrevrange(redis_key, start, end, True)
        if rst:
            return [{'room_id': d[0], 'increase': d[1]} for d in rst]
        else:
            return []

    @classmethod
    def search_by_name_or_tag(cls, query):
        db = DbManager().db
        rooms = set()
        sql = 'select * from {table} where name like %s'.format(table=cls.table)
        query = "%%%s%%" % query
        rooms_info = db.query(sql, query)
        for room_info in rooms_info:
            rooms.add(cls(**room_info))
        # sql = 'select * from room a, room_tag b, tag c where a.id=b.room_id and b.tag_id=c.id and c.name like %s'
        # rooms_info = db.query(sql, query)
        # for room_info in rooms_info:
        #     rooms.add(cls(
        #         id=room_info.room_id,
        #         creator_id=room_info.creator_id,
        #         name=room_info.name,
        #         intro=room_info.intro,
        #         rent=room_info.rent,
        #         avatar=init_pic_url(room_info.avatar),
        #         limit_user_number=room_info.limit_user_number,
        #         status=room_info.status,
        #         create_time=room_info.create_time,
        #         update_time=room_info.update_time,
        #     ))

        return rooms

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        room_lists = db.query(sql)
        return room_lists and [cls(**room) for room in room_lists]

    def get_reward_rank(self, start, count):
        cache = CacheManager().cache
        redis_key = ROOM_USER_REWARD_CACHE_KEY % self.id
        end = start + count - 1
        rst = cache.zrevrange(redis_key, start, end, True)
        if rst:
            return [{'user_id': info[0], 'amount': info[1]} for info in rst]
        else:
            return []

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        r = db.execute(sql)
        self.flush_redis_room_info()
        return r

    def get_users_by_serial_number(self, start, end):
        cache = CacheManager().cache
        cache_key = ROOM_USER_CACHE_KEY % self.id
        user_ids = cache.zrevrange(cache_key, start, end)
        return user_ids and [User.get(user_id) for user_id in user_ids]

    def flush_redis_room_info(self):
        cache = CacheManager().cache
        key = ROOM_CACHE_KEY % self.id
        cache.delete(key)

    def get_users(self, start, count):
        cache = CacheManager().cache
        cache_key = ROOM_USER_CACHE_KEY % self.id
        end = start + count - 1
        user_ids = cache.zrange(cache_key, start, end)
        return user_ids and [User.get(user_id) for user_id in user_ids]

    def jsonify(self, user=None):
        from starmachine.model.room_user import RoomUser
        last_content_updated = self.last_content_updated
        if isinstance(last_content_updated, basestring):
            if last_content_updated == 'None':
                last_content_updated = ''
        else:
            if last_content_updated:
                last_content_updated = last_content_updated.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_content_updated = ''

        data = {
            'id': self.id,
            'creator': {
                'id': self.creator.id,
                'name': self.creator.user_name,
                'avatar': self.creator.avatar_url
            },
            'name': self.name,
            'intro': self.intro,
            'avatar_url': self.avatar_url,
            'limit_user_number': int(self.limit_user_number),
            'status': self.status,
            'user_amount': self.user_amount,
            'balance': self.star_fund,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                            self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'tags': [tag.jsonify() for tag in self.tags if tag],
            'last_content_updated': last_content_updated,
            'admin_users': RoomUser.get_admin_users_by_room(self.id),
        }
        room_users = RoomUser.get_ordered_room_users_by_room(self.id)
        room_users_data = []
        for room_user in room_users:
            user_obj = User.get(room_user.user_id)
            room_users_data.append({
                'id': user_obj.id,
                'name': user_obj.user_name,
                'avatar': user_obj.avatar_url,
                'status': user_obj.status,
            })
        data.update({
            'users': room_users_data,
        })

        if int(self.status) == ROOM_PRIVATE_NEED_VERIFY:
            question_info = RoomQuestion.get_question_by_room(self.id)
            if question_info:
                data.update({
                    'question_info': question_info.jsonify()
                })

        if user:
            from starmachine.model.room_user import RoomUser, RoomBlackUser
            data.update({
                'owner': bool(int(self.creator_id) == int(user.id)),
                'joined': bool(RoomUser.room_exists_user(self.id, user.id)),
                'is_black': bool(RoomBlackUser.is_room_black_user(self.id, user.id)),
            })

        return data


class RoomQuestion(object):

    table = 'room_question'

    def __init__(self, id=None, room_id=None, name=None, create_time=None):
        self.id = id
        self.room_id = room_id
        self.name = name
        self.create_time = create_time

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, room_id, name, create_time):
        db = DbManager().db
        sql = 'insert into {table} (room_id, name, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, room_id, name, create_time)

    @classmethod
    def get_question_by_room(cls, room_id):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s'.format(table=cls.table)
        question_info = db.get(sql, room_id)
        return question_info and cls(**question_info)

    def jsonify(self):
        options = RoomQuestionOption.get_options_by_question(self.id)
        random.shuffle(options)
        return {
            'id': self.id,
            'question_name': self.name,
            'options': [option.jsonify() for option in options],
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }


class RoomQuestionOption(object):

    table = 'room_question_option'

    def __init__(self, id=None, question_id=None, text=None, is_right_answer=None):
        self.id = id
        self.question_id = question_id
        self.text = text
        self.is_right_answer = is_right_answer

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        rst = db.get(sql, id)
        return rst and cls(**rst)

    @classmethod
    def add(cls, question_id, text, is_right_answer):
        db = DbManager().db
        sql = 'insert into {table} (question_id, text, is_right_answer) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, question_id, text, is_right_answer)

    @classmethod
    def get_options_by_question(cls, question_id):
        db = DbManager().db
        sql = 'select * from {table} where question_id=%s'.format(table=cls.table)
        options = db.query(sql, question_id)
        return options and [cls(**option) for option in options]

    def jsonify(self):
        return {
            'id': self.id,
            'text': self.text,
            'is_right_answer': self.is_right_answer,
        }