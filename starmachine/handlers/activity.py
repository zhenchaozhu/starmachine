# # coding: utf-8
#
# from __future__ import division
# import json
# import logging
# from tornado.web import MissingArgumentError
# from starmachine.handlers.base import APIBaseHandler
# from starmachine.lib.utils import check_access_token
# from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, ROOM_NOT_FOUND, SYSTEM_ERROR, ACCESS_NOT_ALLOWED,\
#      ACTIVITY_HAS_JOINED, ACTIVITY_NOT_FOUND, ACTIVITY_OPTION_NOT_FOUND, ACTIVITY_NOT_JOINED
# from starmachine.model.content.activity import Activity, ActivityOption, ActivityResult
# from starmachine.model.user import User
# from starmachine.model.room import Room
# from starmachine.model.order.activity_order import ActivityOrder
# from starmachine.model.consts import ACTIVITY_OPTION_FIXED, ACTIVITY_OPTION_UNLIMITED, ACTIVITY_OPTION_FREE, STATUS_COMPLETE
#
# logger = logging.getLogger(__name__)
#
# class ActivityHandler(APIBaseHandler):
#
#     @check_access_token
#     def post(self):
#         try:
#             user_id = self.get_argument('user_id')
#             room_id = self.get_argument('room_id')
#             activity_type = self.get_argument('activity_type')
#             name = self.get_argument('name')
#             images = self.get_argument('images')
#             intro = self.get_argument('intro')
#             start_time = self.get_argument('start_time')
#             deadline = self.get_argument('deadline')
#             filter = self.get_argument('filter')
#             need_address = self.get_argument('need_address')
#             can_share = self.get_argument('can_share')
#         except MissingArgumentError:
#             return self.error(MISSING_PARAMS)
#
#         user = User.get(user_id)
#         if not user:
#             return self.error(USER_NOT_FOUND)
#
#         room = Room.get(room_id)
#         if not room:
#             return self.error(ROOM_NOT_FOUND)
#
#         try:
#             activity = Activity.add(user_id, room_id, activity_type, name, images, intro, start_time, deadline, filter,
#             need_address, can_share)
#         except Exception as e:
#             logger.error(u'创建活动失败。Error:[%s]' % e)
#             return self.error(SYSTEM_ERROR)
#
#         return self.render({
#             'status': 0,
#             'data': activity.jsonify(),
#         })
#
#
#     @check_access_token
#     def delete(self):
#         try:
#             activity_id = self.get_argument('activity_id')
#         except MissingArgumentError:
#             return self.error(MISSING_PARAMS)
#
#         activity = Activity.get(activity_id)
#         if not activity:
#             return self.error(ACTIVITY_NOT_FOUND)
#
#         activity_orders = ActivityOrder.gets_complete_order_by_activity(activity_id)
#         try:
#             for activity_order in activity_orders:
#                 activity_order.refund()
#         except Exception as e:
#             logger.error(u'')
#             return self.error(SYSTEM_ERROR)
#
# class ActivityOptionHandler(APIBaseHandler):
#
#     @check_access_token
#     def post(self):
#         try:
#             user_id = int(self.get_argument('user_id'))
#             activity_id = self.get_argument('activity_id')
#             option_type = int(self.get_argument('option_type'))
#             options = self.get_argument('options')
#         except MissingArgumentError:
#             return self.error(MISSING_PARAMS)
#
#         options = json.loads(options)
#         user = User.get(user_id)
#         if not user:
#             return self.error(USER_NOT_FOUND)
#
#         activity = Activity.get(activity_id)
#         if int(activity.creator_id) != user_id:
#             return self.error(ACCESS_NOT_ALLOWED)
#
#         if int(option_type) not in [ACTIVITY_OPTION_FIXED, ACTIVITY_OPTION_UNLIMITED]:
#             return self.error(ACCESS_NOT_ALLOWED)
#
#         try:
#             activity.add_options(option_type, options)
#             return self.render({
#                 'status': 0,
#             })
#         except Exception as e:
#             logger.error(u'添加活动选项失败。Error:[%s]' % e)
#             return self.error(SYSTEM_ERROR)
#
#
# class ActivityReleaseHandler(APIBaseHandler):
#
#     @check_access_token
#     def post(self):
#         try:
#             activity_id = self.get_argument('activity_id')
#             star_fund = self.get_argument('star_fund')
#             reduce_price = self.get_argument('reduce_price')
#         except MissingArgumentError:
#             return self.error(MISSING_PARAMS)
#
#         activity = Activity.get(activity_id)
#         if not activity:
#             return self.error(ACTIVITY_NOT_FOUND)
#
#         try:
#             activity.release(star_fund, reduce_price)
#             return self.render({
#                 'status': 0,
#             })
#         except Exception as e:
#             logger.error(u'发布活动失败。Error:[%s]' % e)
#             return self.error(SYSTEM_ERROR)
#
#
# class ActivityJoinHandler(APIBaseHandler):
#
#     @check_access_token
#     def post(self):
#         try:
#             user_id = self.get_argument('user_id')
#             activity_id = self.get_argument('activity_id')
#             option_id = self.get_argument('option_id')
#             amount = self.get_argument('amount')
#             trades_info = self.get_argument('trades_info', None)
#             user_address_id = self.get_argument('user_address_id', None)
#         except MissingArgumentError:
#             return self.error(MISSING_PARAMS)
#
#         if trades_info:
#             trades_info = json.loads(trades_info)
#
#         user = User.get(user_id)
#         if not user:
#             return self.error(USER_NOT_FOUND)
#
#         activity = Activity.get(activity_id)
#         if not activity:
#             return self.error(ACTIVITY_NOT_FOUND)
#
#         option = ActivityOption.get(option_id)
#         if not option:
#             return self.error(ACTIVITY_OPTION_NOT_FOUND)
#
#         if int(option.activity_id) != int(activity_id):
#             return self.error(ACCESS_NOT_ALLOWED)
#
#         if ActivityResult.has_joined(option_id, user_id):
#             return self.error(ACTIVITY_HAS_JOINED)
#
#         try:
#             activity_order = ActivityOrder.add(user_id, activity_id, option_id, user_address_id, amount, trades_info)
#             if option.is_free:
#                 activity_order.free_order_complete()
#
#             return self.render({
#                 'status': 0,
#                 'data': activity_order.jsonify(),
#             })
#         except Exception as e:
#             logger.error(u'创建活动订单失败。Error:[%s]' % e)
#             return self.error(SYSTEM_ERROR)
#
#
# class ActivityQuitHandler(APIBaseHandler):
#
#     @check_access_token
#     def post(self):
#         try:
#             user_id = self.get_argument('user_id')
#             activity_id = self.get_argument('activity_id')
#             option_id = self.get_argument('option_id')
#         except MissingArgumentError:
#             return self.error(MISSING_PARAMS)
#
#         user = User.get(user_id)
#         if not user:
#             return self.error(USER_NOT_FOUND)
#
#         activity = Activity.get(activity_id)
#         if not activity:
#             return self.error(ACTIVITY_NOT_FOUND)
#
#         activity_order = ActivityOrder.get_by_option_and_user(option_id, user_id)
#         if activity_order.status != STATUS_COMPLETE:
#             return self.error(ACTIVITY_NOT_FOUND)
#
#         try:
#             activity_order.refund()
#             return self.render({
#                 'status': 0,
#             })
#         except Exception as e:
#             logger.error(u'退出活动失败。Error:[%s]' % e)
#             return self.error(SYSTEM_ERROR)
#
#
#
#
#
#
#
#
#
#
