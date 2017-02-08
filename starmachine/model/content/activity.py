# # coding: utf-8
#
# from __future__ import division
# import json
# import logging
# from datetime import datetime
# from starmachine.lib.query import DbManager
# from starmachine.lib.redis_cache import CacheManager
# from starmachine.lib.utils import get_int_date
# from starmachine.model.consts import CONTENT_PUBLIC, ACTIVITY_NORMAL, ACTIVITY_OPTION_FIXED, \
#     ACTIVITY_UNPUBLISHED, ACTIVITY_PUBLISHED, ACTIVITY_USER_CACHE_KEY, ACTIVITY_OPTION_USER_CACHE_KEY, \
#     USER_ACTIVITY_OPTION_CACHE_KEY, ACTIVITY_OPTION_FREE
# from starmachine.model.content import Content
# from starmachine.jobs.user import user_join_activity
#
# logger = logging.getLogger(__name__)
#
# class Activity(object):
#
#     table = 'activity'
#
#     def __init__(self, id=None, creator_id=None, room_id=None, activity_type=None, name=None, images=None, intro=None,
#         start_time=None, deadline=None, filter=None, need_address=None, can_share=None, option_type=None, star_fund=None,
#         reduce_price=None, status=None, create_time=None, update_time=None):
#         self.id = id
#         self.creator_id = creator_id
#         self.room_id = room_id
#         self.activity_type = activity_type
#         self.name = name
#         self.images = images
#         self.intro = intro
#         self.start_time = start_time
#         self.deadline = deadline
#         self.filter = filter
#         self.need_address = need_address
#         self.can_share = can_share
#         self.option_type = option_type
#         self.star_fund = star_fund
#         self.reduce_price = reduce_price
#         self.status = status
#         self.create_time = create_time
#         self.update_time = update_time
#
#     def __repr__(self):
#         return '<Activity:id=%s>' % (self.id)
#
#     @classmethod
#     def add(cls, creator_id, room_id, activity_type, name, images, intro, start_time, deadline, filter,
#         need_address, can_share, option_type=ACTIVITY_OPTION_FIXED, star_fund=0, reduce_price=0, status=ACTIVITY_UNPUBLISHED):
#         db = DbManager().db
#         create_time = datetime.now()
#         db.execute('begin;')
#         try:
#             sql = 'insert into {table} (creator_id, room_id, content_type, status, create_time, last_comment_time) ' \
#             'values (%s, %s, %s, %s, %s, %s)'.format(table=Content.table)
#             content_id = db.execute(sql, creator_id, room_id, ACTIVITY_TYPE, CONTENT_PUBLIC, create_time, create_time)
#             sql = 'insert into {table} (id, creator_id, room_id, activity_type, name, images, intro, start_time, ' \
#             'deadline, filter, need_address, can_share, option_type, star_fund, status, create_time) values (%s, %s, ' \
#             '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
#             db.execute(sql, content_id, creator_id, room_id, activity_type, name, images, intro, start_time, deadline,
#             filter, need_address, can_share, option_type, star_fund, status, create_time)
#             db.execute('commit;')
#             return cls.get(content_id)
#         except:
#             db.execute('rollback;')
#             raise
#
#     @classmethod
#     def get(cls, id):
#         db = DbManager().db
#         sql = 'select * from {table} where id=%s'.format(table=cls.table)
#         activity_info = db.get(sql, id)
#         return activity_info and cls(**activity_info)
#
#     def delete(self):
#         db = DbManager().db
#         db.execute('begin;')
#         try:
#             sql = 'delete from {table} where id=%s'.format(table=self.table)
#             db.execute(sql, self.id)
#             sql = 'delete from {table} where id=%s'.format(table=Content.table)
#             db.execute(sql, self.id)
#             db.execute('commit;')
#         except:
#             db.execute('rollback;')
#             raise
#
#     def add_options(self, option_type, options):
#         db = DbManager().db
#         create_time = datetime.now()
#         db.execute('begin;')
#         try:
#             sql = 'update {table} set option_type=%s, update_time=%s where id=%s'.format(table=self.table)
#             db.execute(sql, option_type, create_time, self.id)
#             if options:
#                 for option in options:
#                     user_amount = option.get('user_amount')
#                     is_free = option.get('is_free')
#                     price = option.get('price')
#                     freight = option.get('freight')
#                     describe = option.get('describe')
#                     images = option.get('images')
#                     sql = 'insert into {table} (activity_id, user_amount, is_free, price, freight, describe, images, create_time) ' \
#                           'values (%s, %s, %s, %s, %s, %s, %s, %s)'.format(table=ActivityOption.table)
#                     db.execute(sql, self.id, user_amount, is_free, price, freight, describe, images, create_time)
#             db.execute('commit;')
#         except:
#             db.execute('rollback;')
#             raise
#
#     def release(self, star_fund, reduce_price):
#         db = DbManager().db
#         db.execute('begin;')
#         try:
#             sql = 'update {table} set status=%s, star_fund=%s, reduce_price=%s where id=%s'.format(table=self.table)
#             db.execute(sql, ACTIVITY_PUBLISHED, star_fund, reduce_price, self.id)
#             sql = 'insert into {table} (activity_id, account) values (%s, %s)'.format(table=ActivityAccount.table)
#             db.execute(sql, self.id, 0.00)
#             db.execute('commit;')
#         except:
#             db.execute('rollback;')
#             raise
#
#     def jsonify(self, user=None):
#         options = ActivityOption.get_options_by_activity(self.id)
#         return {
#             'id': self.id,
#             'creator_id': self.creator_id,
#             'room_id': self.room_id,
#             'name': self.name,
#             'intro': self.intro,
#             'options': [option.jsonify() for option in options],
#             'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
#             'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
#             'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
#         }
#
#
# # 活动基金
# class ActivityAccount(object):
#
#     table = 'activity_account'
#
#     def __init__(self, id, activity_id, balance):
#         self.id = id
#         self.activity_id =activity_id
#         self.balance = balance
#
#     @classmethod
#     def add(cls, activity_id, balance):
#         db = DbManager().db
#         sql = 'insert into {table} (activity_id, balance) values (%s, %s)'.format(table=cls.table)
#         db.execute(sql, activity_id, balance)
#
#
# class ActivityOption(object):
#
#     table = 'activity_option'
#
#     def __init__(self, id, activity_id, user_amount, is_free, price, freight, describe, images, create_time):
#         self.id = id
#         self.activity_id = activity_id
#         self.user_amount = user_amount
#         self._is_free = is_free
#         self.price = price
#         self.freight = freight
#         self.describe = describe
#         self.images = images
#         self.create_time = create_time
#
#     @property
#     def is_free(self):
#         return int(self.is_free) == ACTIVITY_OPTION_FREE
#
#     @classmethod
#     def add(cls, activity_id, user_amount, is_free, price, freight, describe, images):
#         db = DbManager().db
#         create_time = datetime.now()
#         sql = 'insert into {table} (activity_id, user_amount, is_free, price, freight, describe, images, create_time) ' \
#         'values (%s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
#         db.execute(sql, activity_id, user_amount, is_free, price, freight, describe, images, create_time)
#
#     @classmethod
#     def get(cls, id):
#         db = DbManager().db
#         sql = 'select * from {table} where id=%s'.format(table=cls.table)
#         option = db.get(sql, id)
#         return option and cls(**option)
#
#     @classmethod
#     def get_options_by_activity(cls, activity_id):
#         db = DbManager().db
#         sql = 'select * from {table} where activity_id=%s'.format(table=cls.table)
#         options = db.query(sql, activity_id)
#         return options and [cls(**option) for option in options]
#
#     def jsonify(self):
#         return {
#             'id': id,
#             'user_amount': self.user_amount,
#             'is_free': self.is_free,
#             'price': self.price,
#             'freight': self.freight,
#             'describe': self.describe,
#             'images': self.images,
#             'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
#         }
#
#
# class ActivityResult(object):
#
#     table = 'activity_result'
#
#     def __init__(self, id, activity_id, option_id, user_id, join_time):
#         self.id = id
#         self.activity_id = activity_id
#         self.option_id = option_id
#         self.user_id = user_id
#         self.join_time = join_time
#
#     @classmethod
#     def add(cls, activity_id, option_id, user_id):
#         join_time = datetime.now()
#         cache = CacheManager().cache
#         activity_user_key = ACTIVITY_USER_CACHE_KEY % activity_id
#         activity_option_user_key = ACTIVITY_OPTION_USER_CACHE_KEY % option_id
#         user_activity_option_id = USER_ACTIVITY_OPTION_CACHE_KEY % user_id
#         score = get_int_date(join_time)
#         try:
#             cache.zadd(activity_user_key, score, user_id)
#             cache.zadd(activity_option_user_key, score, user_id)
#             cache.zadd(user_activity_option_id, score, option_id)
#             logger.info(u'添加用户活动关系到redis成功。')
#         except Exception as e:
#             logger.error(u'添加用户活动关系到redis失败。Error:[%s]' % e)
#             raise
#
#         user_join_activity.delay(activity_id, option_id, user_id, join_time)
#         return
#
#     @classmethod
#     def add_to_mysql(cls, activity_id, option_id, user_id, join_time):
#         db = DbManager().db
#         sql = 'insert into {table} (activity_id, option_id, user_id, join_time) values (%s, %s, %s, %s)'.format(table=cls.table)
#         try:
#             db.execute(sql, activity_id, option_id, user_id, join_time)
#             logger.info(u'添加活动用户关系到mysql成功。')
#         except Exception as e:
#             logger.error(u'添加活动用户关系到mysql失败。Error:[%s]', e)
#             raise
#
#         return
#
#     @classmethod
#     def delete_by_activity(cls, activity_id):
#         activity_user_key = ACTIVITY_USER_CACHE_KEY % activity_id
#         db = DbManager().db
#         sql = 'select * from {table} where activity_id=%s'.format(table=cls.table)
#         activity_users = db.query(sql, activity_id)
#
#         for activity_user in activity_users:
#             pass
#
#
#     @classmethod
#     def has_joined(cls, option_id, user_id):
#         db = DbManager().db
#         sql = 'select id from {table} where option_id=%s and user_id=%s'.format(table=cls.table)
#         try:
#             return db.query(sql, option_id, user_id)[0]
#         except:
#             return None
#
#     @classmethod
#     def quit(cls, activity_id, option_id, user_id):
#         cache = CacheManager().cache
#         db = DbManager().db
#         activity_user_key = ACTIVITY_USER_CACHE_KEY % activity_id
#         activity_option_user_key = ACTIVITY_OPTION_USER_CACHE_KEY % option_id
#         user_activity_option_id = USER_ACTIVITY_OPTION_CACHE_KEY % user_id
#         with cache.pipeline() as pipe:
#             pipe.zrem(activity_user_key, user_id)
#             pipe.zrem(activity_option_user_key, user_id)
#             pipe.zrem(user_activity_option_id, option_id)
#             rs = pipe.execute()
#             rs = filter(lambda x: x!=0, rs)
#             if False in rs:
#                 logger.error(u'从缓存中删除用户参加活动数据失败。Option:[%s], User:[%s]' % (option_id, user_id))
#
#         sql = 'delete from {table} where option_id=%s and user_id=%s'.format(table=cls.table)
#         db.execute(sql, option_id, user_id)
