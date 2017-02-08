# coding: utf-8

import logging
from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.utils import redis_cache_obj, init_pic_url
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.user_tag import UserTag
from starmachine.model.consts import USER_CREATED_ROOM_KEY, USER_ROOM_CACHE_KEY
from starmachine.model.city import City
from starmachine.model.consts import USER_DEFAULT_CITY, USER_DEFAULT_ROLE, USER_NORMAL, USER_ADMIN, USER_FOLLOW_KEY, USER_FANS_KEY
from starmachine.model.rong import UserChatStatus
from starmachine.model.flower_user import FlowerUser
from starmachine.model.group_seeds import GroupSeeds
from starmachine.model.group_envelope import GroupEnvelope

logger = logging.getLogger(__name__)
USER_CACHE_KEY = 'user:%s'

class User(object):

    table = 'user'

    def __init__(self, id=None, telephone=None, password=None, name=None, role=None, avatar=None, intro=None,
        city_id=None, status=None, create_time=None, update_time=None):
        self.id = id
        self.telephone = telephone
        self.password = password
        self.name = name
        self.role = role
        self.avatar = avatar
        self.intro = intro
        self.city_id = city_id
        self.status = status
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<User:id=%s>' % (self.id)

    @property
    def super_user(self):
        return int(self.status) == USER_ADMIN

    @property
    def city(self):
        return City.get(self.city_id)

    @property
    def user_name(self):
        return self.name if self.name else u'事大用户*%s' % str(self.id)[-2:]

    @property
    def tags(self):
        from starmachine.model.user_tag import UserTag
        return UserTag.get_tags_by_user(self.id)

    @property
    def account(self):
        from starmachine.model.account import Account
        account =  Account.get_by_user(self.id)
        if not account:
            account = Account.add(self.id, 0.00)

        return account

    @property
    def created_rooms(self):
        from starmachine.model.room import Room
        cache = CacheManager().cache
        cache_key = USER_CREATED_ROOM_KEY % self.id
        room_ids = list(cache.smembers(cache_key))
        return room_ids and [Room.get(room_id).jsonify(self) for room_id in room_ids]

    @property
    def joined_rooms_count(self):
        cache = CacheManager().cache
        cache_key = USER_ROOM_CACHE_KEY % self.id
        return cache.zcard(cache_key)

    @property
    def receive_reward_amount(self):
        from starmachine.model.order.reward_order import RewardOrder
        return float(RewardOrder.get_user_receive_reward_amount(self.id))

    @property
    def avatar_url(self):
        return init_pic_url(self.avatar)

    @property
    def fans_amount(self):
        cache = CacheManager().cache
        redis_key = USER_FANS_KEY % self.id
        return cache.zcard(redis_key)

    @property
    def follow_amount(self):
        cache = CacheManager().cache
        redis_key = USER_FOLLOW_KEY % self.id
        return cache.zcard(redis_key)

    @classmethod
    @redis_cache_obj(USER_CACHE_KEY)
    def get(cls, uid):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        user_info = db.get(sql, uid)
        return user_info and cls(**user_info)

    @classmethod
    def get_user_by_telephone(cls, telephone):
        db = DbManager().db
        sql = 'select * from {table} where telephone=%s'.format(table=cls.table)
        user_info = db.get(sql, telephone)
        return user_info and cls(**user_info)

    @classmethod
    def add(cls, telephone, password, name='', role=USER_DEFAULT_ROLE, avatar='', intro='', city_id=USER_DEFAULT_CITY,
        status=USER_NORMAL):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (telephone, password, name, role, avatar, intro, city_id, status, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        try:
            user_id = db.execute(sql, telephone, password, name, role, avatar, intro, city_id, status, create_time)
            logger.info(u'添加用户成功。user_id:[%s]' % user_id)
            return user_id
        except Exception as e:
            logger.error(u'添加用户失败。Error:[%s]' % e)
            raise

    @classmethod
    def exists_user_by_telephone(cls, telephone):
        db = DbManager().db
        sql = 'select id from {table} where telephone=%s'.format(table=cls.table)
        try:
            return db.query(sql, telephone)[0]
        except:
            return None

    @classmethod
    def exists_user_name(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None

    @classmethod
    def get_user_count(cls):
        db = DbManager().db
        sql = 'select count(id) from {table}'.format(table=cls.table)
        count = db.get(sql)
        if count and count.get('count(id)'):
            return count.get('count(id)')
        else:
            return 0

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        r = db.execute(sql)
        self.flush_redis_user_info()
        return r

    def add_user_info(self, avatar, name, tag_ids):
        db = DbManager().db
        update_time = datetime.now()
        try:
            sql = 'update {table} set avatar=%s, name=%s, update_time=%s where id=%s'.format(table=self.table)
            db.execute(sql, avatar, name, update_time, self.id)
            UserTag.add(self.id, tag_ids)

            self.flush_redis_user_info()
        except Exception as e:
            logger.warning(u'添加用户信息失败。User:[%s], Error:[%s]' % (self.id, e))
            raise

    def has_room_access(self, room_id):
        from starmachine.model.room_user import RoomUser
        from starmachine.model.room import Room
        room = Room.get(room_id)
        if self.super_user:
            return True

        if int(room.creator_id) == int(self.id):
            return True

        if RoomUser.room_exists_user(room_id, self.id):
            return True

        return False

    def has_room_speak_access(self, room_id):
        from starmachine.model.room_user import RoomUser
        if RoomUser.is_room_silent_user(room_id, self.id):
            return False

        return True

    def has_room_create_welfare_access(self, room):
        from starmachine.model.room_user import RoomUser
        if int(room.creator_id) == int(self.id) or RoomUser.is_room_admin(room.id, self.id):
            return True

        return False

    def flush_redis_user_info(self):
        cache = CacheManager().cache
        key = USER_CACHE_KEY % self.id
        cache.delete(key)

    def jsonify(self):
        from starmachine.model.user_validate import UserValidate
        address_list = UserAddress.gets_by_user(self.id)
        user_validate = UserValidate.get_by_user_id(self.id)
        user_payment_code = UserPaymentCode.get_by_user(self.id)
        account = self.account
        balance = account.balance
        flower_user = FlowerUser.get_by_user(self.id)
        data = {
            'id': self.id,
            'telephone': self.telephone,
            'name': self.user_name,
            'role': self.role,
            'avatar': self.avatar_url,
            'intro': self.intro,
            'city': self.city.jsonify(),
            'status': self.status,
            'join_rooms_count': self.joined_rooms_count,
            'created_rooms': self.created_rooms,
            'address_list': [address.jsonify() for address in address_list],
            'tags': [tag.jsonify() for tag in self.tags if tag],
            'balance': float(balance) if balance else 0,
            'validate_status': user_validate.status if user_validate else '',
            'has_payment_code': True if user_payment_code else False,
            'receive_reward_amount': self.receive_reward_amount,
            'fans_amount': self.fans_amount,
            'follow_amount': self.follow_amount,
            'flower_user_info': flower_user.jsonify() if flower_user else None,
        }
        if flower_user:
            flower_identity = UserChatStatus.is_flower_identity(self.id)
        else:
            flower_identity = False

        data.update({
            'flower_identity': flower_identity
        })

        return data


class UserAddress(object):

    table = 'user_address'

    def __init__(self, id=None, user_id=None, district=None, name=None, telephone=None, address=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.district = district
        self.name = name
        self.telephone = telephone
        self.address = address
        self.create_time = create_time
        self.update_time = update_time

    @property
    def creator(self):
        return User.get(self.user_id)

    @classmethod
    def add(cls, user_id, district, name, telephone, address):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, district, name, telephone, address, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        user_address_id = db.execute(sql, user_id, district, name, telephone, address, create_time)
        return user_address_id and cls(user_address_id, user_id, district, name, telephone, address, create_time, None)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        user_address_info = db.get(sql, id)
        return user_address_info and cls(**user_address_info)

    @classmethod
    def gets_by_user(cls, user_id, start=0, count=10):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s order by create_time desc limit %s, %s'.format(table=cls.table)
        address_list = db.query(sql, user_id, start, count)
        return address_list and [cls(**address) for address in address_list]

    def delete(self):
        db = DbManager().db
        sql = 'delete from {table} where id=%s'.format(table=self.table)
        db.execute(sql, self.id)

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        db.execute(sql)

    def jsonify(self):
        return {
            'id': self.id,
            'name': self.name,
            'telephone': self.telephone,
            'district': self.district,
            'address': self.address,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                            self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }


class UserPaymentCode(object):

    table = 'user_payment_code'

    def __init__(self, id=None, user_id=None, payment_code=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.payment_code = payment_code
        self.create_time = create_time
        self.update_time = update_time

    @classmethod
    def add(cls, user_id, payment_code):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, payment_code, create_time) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, payment_code, create_time)

    @classmethod
    def get_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        user_payment_info = db.get(sql, user_id)
        return user_payment_info and cls(**user_payment_info)

    def update_payment_code(self, payment_code, change_time):
        db = DbManager().db
        sql = 'update {table} set payment_code=%s, update_time=%s where id=%s'.format(table=self.table)
        db.execute(sql, payment_code, change_time, self.id)


class UserBind(object):

    table = 'user_bind'

    def __init__(self, id=None, user_id=None, wx_id=None):
        self.id = id
        self.user_id = user_id
        self.wx_id = wx_id

    @classmethod
    def bind_wx(cls, user_id, wx_id):
        db = DbManager().db
        sql = 'insert into {table} (user_id, wx_id) values (%s, %s)'.format(table=cls.table)
        db.execute(sql, user_id, wx_id)

    @classmethod
    def get_by_wx(cls, wx_id):
        db = DbManager().db
        sql = 'select * from {table} where wx_id=%s'.format(table=cls.table)
        user_bind = db.get(sql, wx_id)
        return user_bind and cls(**user_bind)