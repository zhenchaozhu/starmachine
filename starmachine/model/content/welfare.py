# coding: utf-8

import json
from datetime import datetime
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.query import DbManager
from starmachine.lib.utils import init_pic_url
from starmachine.model.content import Content
from starmachine.model.star_fund import StarFund
from starmachine.model.consts import WELFARE_TYPE, CONTENT_PUBLIC, WELFARE_ROB_UNDER_WAY, WELFARE_ROB_END, \
    STAR_FUND_WELFARE_EXPAND, WELFARE_TYPE_SPECIAL, CONTENT_LIKED_RANK_KEY, CONTENT_COMMENT_CACHE_KEY, \
    CONTENT_REWARD_CACHE_KEY, CONTENT_REWARD_AMOUNT_CACHE_KEY, WELFARE_ORDER_DELIVER, WELFARE_POSTAGE, WELFARE_ROB_END_AND_DELIVERY
from starmachine.handlers.exception import StarFundInsufficient
from starmachine.model.order.welfare_order import WelfareOrder
from starmachine.model.user import User
from starmachine.model.content.content_like import ContentLiked
from starmachine.model.star_fund import StarFund
from starmachine.model.star_fund_record import StarFundRecord
from starmachine.model.room_user import RoomUser
from starmachine.model.room import Room

class Welfare(object):

    table = 'welfare'

    def __init__(self, id=None, creator_id=None, room_id=None, welfare_type=None, price=None, count=None, name=None,
        start_time=None, deadline=None, images=None, status=None, create_time=None, update_time=None):
        self.id = id
        self.creator_id = creator_id
        self.room_id = room_id
        self.welfare_type = welfare_type
        self.price = price
        self.count = count
        self.name = name
        self.start_time = start_time
        self.deadline = deadline
        self.images = images
        self.status = status
        self.create_time = create_time
        self.update_time = update_time

    @property
    def creator(self):
        return User.get(self.creator_id)

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
    def reward_amount(self):
        cache = CacheManager().cache
        reward_amount = cache.zscore(CONTENT_REWARD_AMOUNT_CACHE_KEY, self.id)
        return reward_amount if reward_amount else 0

    @property
    def robed_user_amount(self):
        robed_user_amount = WelfareOrder.get_robers_count(self.id)
        return robed_user_amount

    @property
    def expired(self):
        now = datetime.now()
        if isinstance(self.deadline, datetime):
            return self.deadline < now
        else:
            return self.deadline < now.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def add(cls, creator_id, room_id, welfare_type, price, count, name, start_time, deadline, images, room_user_status,
        amount, content_status=CONTENT_PUBLIC, welfare_status=WELFARE_ROB_UNDER_WAY):
        create_time = datetime.now()
        room = Room.get(room_id)
        star_fund = StarFund.get_by_room(room_id)
        if float(star_fund.balance) < amount:
            raise StarFundInsufficient

        db = DbManager().db
        db.execute('begin;')
        try:
            sql = 'insert into {table} (creator_id, room_id, content_type, status, create_time, last_comment_time, room_user_status) values' \
                  ' (%s, %s, %s, %s, %s, %s, %s)'.format(table=Content.table)
            content_id = db.execute(sql, creator_id, room_id, WELFARE_TYPE, content_status, create_time, create_time, room_user_status)
            sql = 'insert into {table} (id, creator_id, room_id, welfare_type, price, count, name, start_time, deadline, images, status, ' \
                'create_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
            db.execute(sql, content_id, creator_id, room_id, welfare_type, price, count, name, start_time, deadline, images,
                welfare_status, create_time)
            sql = 'update {table} set balance=balance-%s where room_id=%s'.format(table=StarFund.table)
            db.execute(sql, amount, room_id)
            sql = 'insert into {table} (room_id, source, amount, create_time, extra, extra_info) values (%s, %s, %s, %s, %s, %s)'.\
                format(table=StarFundRecord.table)
            db.execute(sql, room_id, STAR_FUND_WELFARE_EXPAND, -amount, create_time, content_id, name)
            db.execute('commit;')
        except:
            db.execute('rollback;')
            raise

        room.update(last_content_updated=create_time, update_time=create_time)
        return cls.get(content_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        welfare_info = db.get(sql, id)
        return welfare_info and cls(**welfare_info)

    def welfare_robed_end(self):
        db = DbManager().db
        sql = 'update {table} set status=%s where id=%s'.format(table=self.table)
        db.execute(sql, WELFARE_ROB_END, self.id)

    def welfare_delivery(self):
        db = DbManager().db
        sql = 'update {table} set status=%s where id=%s'.format(table=self.table)
        db.execute(sql, WELFARE_ROB_END_AND_DELIVERY, self.id)

    def jsonify(self, user=None):
        data = {
            'id': self.id,
            'creator': {
                'id': self.creator.id,
                'name': self.creator.user_name,
                'avatar': self.creator.avatar_url,
            },
            'content_type': WELFARE_TYPE,
            'price': float(self.price),
            'count': self.count,
            'name': self.name,
            'welfare_type': self.welfare_type,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'reward_amount': self.reward_amount,
            'like_amount': self.like_amount,
            'comment_amount': self.comment_amount,
            'reward_user_amount': self.reward_user_amount,
            'robed_user_amount': self.robed_user_amount,
            'star_fund_pay_amount': float(self.price) * self.count + self.count * WELFARE_POSTAGE,
            'expired': self.expired,
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
            welfare_order = WelfareOrder.get_by_welfare_and_user(self.id, user.id)
            data.update({
                'has_liked': bool(ContentLiked.has_liked(self.id, user.id)),
                'has_robed': True if welfare_order else False,
                'has_delivery': True if welfare_order and welfare_order.status == WELFARE_ORDER_DELIVER else False,
            })

        return data
