# coding: utf-8

import time
import logging
from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.jobs.user import add_room_user, job_delete_room_user
from starmachine.model.room import Room
from starmachine.model.user import User
from starmachine.model.consts import ROOM_USER_CACHE_KEY, USER_ROOM_CACHE_KEY, ROOM_USER_COUNT_KEY, STATUS_REFUNDED, ROOM_INCREASE_RANK_CACHE_KEY
from starmachine.model.star_fund import StarFund
from starmachine.model.account import Account
from starmachine.lib.utils import get_int_date
from starmachine.handlers.exception import StarFundInsufficient
from starmachine.model.consts import ROOM_USER_CREATOR, ROOM_USER_ADMIN, ROOM_USER_NORMAL, ROOM_USER_SILENT

logger = logging.getLogger(__name__)

class RoomUser(object):

    table = 'room_user'

    def __init__(self, id=None, room_id=None, user_id=None, join_time=None, update_time=None, status=None):
        self.id = id
        self.room_id = room_id
        self.user_id = user_id
        self.join_time = join_time
        self.update_time = update_time
        self.status = status

    def __repr__(self):
        return '<RoomUser:id=%s>' % (self.id)

    @classmethod
    def get_by_room_and_user(cls, room_id, user_id):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
        rst = db.get(sql, room_id, user_id)
        return rst and cls(**rst)

    @classmethod
    def add_to_mysql(cls, room_id, user_id, join_time, status):
        db = DbManager().db
        sql = 'insert into {table} (room_id, user_id, join_time, status) values (%s, %s, %s, %s)'.format(table=cls.table)
        try:
            db.execute(sql, room_id, user_id, join_time, status)
            logger.info(u'添加房间用户关系到mysql成功。')
        except Exception as e:
            logger.error(u'添加房间用户关系到mysql失败。Error:[%s]', e)
            raise

        return

    @classmethod
    def add(cls, room_id, user_id, status=ROOM_USER_NORMAL):
        join_time = datetime.now()
        cache = CacheManager().cache
        room_user_key = ROOM_USER_CACHE_KEY % room_id
        user_room_key = USER_ROOM_CACHE_KEY % user_id
        score = get_int_date(join_time)
        try:
            cache.zadd(room_user_key, score, user_id)
            cache.zadd(user_room_key, score, room_id)
            logger.info(u'添加房间用户关系到redis成功。')
        except Exception as e:
            logger.error(u'添加房间关系用户到redis失败。Error:[%s]' % e)
            raise

        add_room_user.delay(room_id, user_id, join_time, status)
        cache.zincrby(ROOM_USER_COUNT_KEY, room_id)
        room_increase_rank_key = ROOM_INCREASE_RANK_CACHE_KEY % (join_time.year, join_time.month)
        cache.zincrby(room_increase_rank_key, room_id, 1)
        return

    @classmethod
    def delete_room_user(cls, room_id, user_id):
        cache = CacheManager().cache
        delete_time = datetime.now()
        room_user_key = ROOM_USER_CACHE_KEY % room_id
        user_room_key = USER_ROOM_CACHE_KEY % user_id
        try:
            cache.zrem(room_user_key, user_id)
            cache.zrem(user_room_key, room_id)
            logger.info(u'从redis中删除房间用户关系成功。')
        except Exception as e:
            logger.error(u'从redis中删除房间用户关系失败。Error:[%s]' % e)
            raise

        job_delete_room_user.delay(room_id, user_id)
        cache.zincrby(ROOM_USER_COUNT_KEY, room_id, -1)
        room_increase_rank_key = ROOM_INCREASE_RANK_CACHE_KEY % (delete_time.year, delete_time.month)
        cache.zincrby(room_increase_rank_key, room_id, -1)
        return

    @classmethod
    def delete_room_user_from_sql(cls, room_id, user_id):
        db = DbManager().db
        sql = 'delete from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
        try:
            db.execute(sql, room_id, user_id)
            logger.info(u'从mysql中删除房间用户关系成功。')
        except Exception as e:
            logger.error(u'从mysql中删除房间用户关系失败。Error:[%s]' % e)
            raise

        return

    @classmethod
    def remove_and_black_user(cls, room_id, user_id):
        remove_time = datetime.now()
        db = DbManager().db
        db.execute('begin;')
        try:
            sql = 'delete from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
            db.execute(sql, room_id, user_id)
            sql = 'insert into {table} (room_id, user_id, create_time) values (%s, %s, %s)'.format(table=RoomBlackUser.table)
            db.execute(sql, room_id, user_id, remove_time)
            db.execute('commit;')
            logger.info(u'在mysql中从房间中移除用户成功。Room:[%s], User:[%s]' % (room_id, user_id))
        except:
            db.execute('rollback;')
            logger.error(u'在mysql中从房间中移除用户失败。Room:[%s], User:[%s]' % (room_id, user_id))
            raise

        cache = CacheManager().cache
        room_user_key = ROOM_USER_CACHE_KEY % room_id
        user_room_key = USER_ROOM_CACHE_KEY % user_id
        try:
            cache.zrem(room_user_key, user_id)
            cache.zrem(user_room_key, room_id)
            logger.info(u'在redis中从房间中移除用户成功。Room:[%s], User:[%s]' % (room_id, user_id))
        except Exception as e:
            logger.error(u'从redis中删除房间用户关系失败。Error:[%s]' % e)
            raise

        cache.zincrby(ROOM_USER_COUNT_KEY, room_id, -1)
        room_increase_rank_key = ROOM_INCREASE_RANK_CACHE_KEY % (remove_time.year, remove_time.month)
        cache.zincrby(room_increase_rank_key, room_id, -1)

    @classmethod
    def get_room_admin_count(cls, room_id):
        db = DbManager().db
        sql = 'select count(id) from {table} where room_id=%s and status=%s'.format(table=cls.table)
        rst = db.get(sql, room_id, ROOM_USER_ADMIN)
        return rst and rst.get('count(id)')

    @classmethod
    def room_exists_user(cls, room_id, user_id):
        cache = CacheManager().cache
        cache_key = ROOM_USER_CACHE_KEY % room_id
        if cache.exists(cache_key):
            return cache.zscore(cache_key, user_id)
        else:
            db = DbManager().db
            sql = 'select id from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
            try:
                return db.query(sql, room_id, user_id)[0]
            except:
                return None

    @classmethod
    def get_user_amount_by_room(cls, room_id):
        cache = CacheManager().cache
        cache_key = ROOM_USER_CACHE_KEY % room_id
        if cache.exists(cache_key):
            return cache.zcard(cache_key)
        else:
            db = DbManager().db
            sql = 'select count(id) from {table} where room_id=%s'.format(table=cls.table)
            return db.get(sql, room_id).get('count(id)')

    @classmethod
    def get_rooms_by_user(cls, user_id, start=0, count=10):
        cache = CacheManager().cache
        cache_key = USER_ROOM_CACHE_KEY % user_id
        end = start + count - 1
        room_ids = cache.zrevrange(cache_key, start, end)
        return room_ids and [Room.get(room_id) for room_id in room_ids]

    @classmethod
    def get_rooms_by_user_order_by_update_time(cls, user_id, start, count):
        db = DbManager().db
        sql = 'select * from room left join room_user on room.id=room_user.room_id where room_user.user_id=%s order by room.update_time desc limit %s, %s'
        room_ids = db.query(sql, user_id, start, count)
        return room_ids and [Room.get(room_id.get('room_id')) for room_id in room_ids]

    @classmethod
    def get_user_ids_by_room(cls, room_id):
        cache = CacheManager().cache
        cache_key = ROOM_USER_CACHE_KEY % room_id
        if cache.exists(cache_key):
            user_ids = cache.zrevrange(cache_key, 0, -1)
            return user_ids
        else:
            db = DbManager().db
            sql = 'select user_id from {table} where room_id=%s'.format(table=cls.table)
            user_ids_dict = db.query(sql, room_id)
            return user_ids_dict and [user_id_dict.get('user_id') for user_id_dict in user_ids_dict]

    @classmethod
    def get_users_by_room(cls, room_id):
        cache = CacheManager().cache
        cache_key = ROOM_USER_CACHE_KEY % room_id
        if cache.exists(cache_key):
            user_ids = cache.zrevrange(cache_key, 0, -1)
            return user_ids and [User.get(user_id) for user_id in user_ids]
        else:
            db = DbManager().db
            sql = 'select user_id from {table} where room_id=%s'.format(table=cls.table)
            user_ids_dict = db.query(sql, room_id)
            return user_ids_dict and [User.get(user_id_dict.get('user_id')) for user_id_dict in user_ids_dict]

    @classmethod
    def get_ordered_room_users_by_room(cls, room_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where room_id=%s order by status, join_time asc limit %s, %s'.format(table=cls.table)
        rst = db.query(sql, room_id, start, count)
        return rst and [cls(**d) for d in rst]

    @classmethod
    def get_admin_users_by_room(cls, room_id):
        db = DbManager().db
        sql = 'select user_id from {table} where room_id=%s and status=%s'.format(table=cls.table)
        user_ids_dict = db.query(sql, room_id, ROOM_USER_ADMIN)
        return user_ids_dict and [user_id_dict.get('user_id') for user_id_dict in user_ids_dict]

    @classmethod
    def set_room_admin(cls, room_id, user_id):
        db = DbManager().db
        update_time = datetime.now()
        sql = 'update {table} set update_time=%s, status=%s where room_id=%s and user_id=%s'.format(table=cls.table)
        db.execute(sql, update_time, ROOM_USER_ADMIN, room_id, user_id)

    @classmethod
    def delete_room_admin(cls, room_id, user_id):
        db = DbManager().db
        update_time = datetime.now()
        sql = 'update {table} set update_time=%s, status=%s where room_id=%s and user_id=%s'.format(table=cls.table)
        db.execute(sql, update_time, ROOM_USER_NORMAL, room_id, user_id)

    @classmethod
    def is_room_admin(cls, room_id, user_id):
        db = DbManager().db
        sql = 'select status from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
        rst = db.get(sql, room_id, user_id)
        try:
            status = rst.get('status')
            return int(status) == ROOM_USER_ADMIN
        except:
            return False

    @classmethod
    def set_user_silent(cls, room_id, user_id, set_time):
        db = DbManager().db
        sql = 'update {table} set update_time=%s, status=%s where room_id=%s and user_id=%s'.format(table=cls.table)
        db.execute(sql, set_time, ROOM_USER_SILENT, room_id, user_id)

    @classmethod
    def remove_user_silent(cls, room_id, user_id, status):
        db = DbManager().db
        update_time = datetime.now()
        sql = 'update {table} set update_time=%s, status=%s where room_id=%s and user_id=%s'.format(table=cls.table)
        db.execute(sql, update_time, status, room_id, user_id)

    @classmethod
    def is_room_silent_user(cls, room_id, user_id):
        db = DbManager().db
        sql = 'select id from {table} where room_id=%s and user_id=%s and status=%s'.format(table=cls.table)
        try:
            return db.query(sql, room_id, user_id, ROOM_USER_SILENT)[0]
        except:
            return None

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        room_user_infos = db.query(sql)
        return room_user_infos and [cls(**room_user_info) for room_user_info in room_user_infos]

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        db.execute(sql)

    def has_room_user_handle_access(self, room_remove_user):
        if self.user_id != room_remove_user.user_id:
            if self.status == ROOM_USER_CREATOR:
                return True

            if self.status == ROOM_USER_ADMIN:
                if room_remove_user.status == ROOM_USER_NORMAL:
                    return True

        return False

# class RoomSilentUser(object):
#
#     table = 'room_silent_user'
#
#     def __init__(self, id, room_id, user_id, create_time):
#         self.id = id
#         self.room_id = room_id
#         self.user_id = user_id
#         self.create_time = create_time
#
#     @classmethod
#     def add(cls, room_id, user_id):
#         db = DbManager().db
#         create_time = datetime.now()
#         sql = 'insert into {table} (room_id, user_id, create_time) values (%s, %s, %s)'.format(table=cls.table)
#         db.execute(sql, room_id, user_id, create_time)


class RoomBlackUser(object):

    table = 'room_black_user'

    def __init__(self, id, room_id, user_id, create_time):
        self.id = id
        self.room_id = room_id
        self.user_id = user_id
        self.create_time = create_time

    @classmethod
    def add(cls, room_id, user_id):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (room_id, user_id, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, room_id, user_id, create_time)

    @classmethod
    def is_room_black_user(cls, room_id, user_id):
        db = DbManager().db
        sql = 'select id from {table} where room_id=%s and user_id=%s'.format(table=cls.table)
        try:
            return db.query(sql, room_id, user_id)[0]
        except:
            return None