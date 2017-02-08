# coding: utf-8

from __future__ import division
import json
import logging
from datetime import datetime, timedelta
# from apscheduler.schedulers.tornado import TornadoScheduler
from tornado.web import MissingArgumentError
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token
from starmachine.lib.tornado_scheduler import tornado_scheduler
from starmachine.handlers.error import MISSING_PARAMS, ROOM_NOT_FOUND, SYSTEM_ERROR, ACCESS_NOT_ALLOWED, \
    ROOM_STAR_FUND_NOT_ENOUGH, WELFARE_NOT_FOUND, WELFARE_HAS_ROBED, WELFARE_HAS_ROBED_OVER, WELFARE_UNDER_WAY, \
    WELFARE_HAS_ALREADY_DELIVERY, WELFARE_HAS_ALREADY_COMPLETE
from starmachine.model.content.welfare import Welfare
from starmachine.model.order.welfare_order import WelfareOrder
from starmachine.model.user import User
from starmachine.model.room import Room
from starmachine.model.room_user import RoomUser
from starmachine.model.star_fund import StarFund
from starmachine.model.consts import ROOM_USER_CREATOR, ROOM_USER_ADMIN, WELFARE_TYPE_SPECIAL, WELFARE_POSTAGE, \
    WELFARE_ROB_UNDER_WAY, WELFARE_ROB_END, WELFARE_ROB_END_AND_DELIVERY
from starmachine.jobs.welfare import welfare_created_notify, welfare_end_notify, welfare_confirm_notify, \
    welfare_ordered_notify, welfare_auto_complete
from starmachine.jobs.integral import handle_daily_create_welfare, handle_daily_rob_welfare

logger = logging.getLogger(__name__)

class WelfareHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        welfare_id = self.get_argument('welfare_id')
        room_id = int(self.get_argument('room_id'))
        welfare = Welfare.get(welfare_id)
        user = User.get(user_id)

        if not welfare:
            return self.error(WELFARE_NOT_FOUND)

        if int(welfare.room_id) != room_id:
            return self.error(ACCESS_NOT_ALLOWED)

        return self.render({
            'status': 0,
            'data': welfare.jsonify(user),
        })


    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            welfare_type = self.get_argument('welfare_type', WELFARE_TYPE_SPECIAL)
            price = float(self.get_argument('price'))
            count = int(self.get_argument('count'))
            name = self.get_argument('name')
            images = self.get_argument('images')
            start_time = self.get_argument('start_time')
            deadline = self.get_argument('deadline')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        star_fund = StarFund.get_by_room(room_id)
        amount = price * count + count * WELFARE_POSTAGE
        if float(star_fund.balance) < amount:
            return self.error(ROOM_STAR_FUND_NOT_ENOUGH)

        room_user = RoomUser.get_by_room_and_user(room_id, user_id)
        if not room_user or not int(room_user.status) in (ROOM_USER_ADMIN, ROOM_USER_CREATOR):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            welfare = Welfare.add(user_id, room_id, welfare_type, price, count, name, start_time, deadline, images, room_user.status, amount)
        except Exception as e:
            logger.error(u'创建福利失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        self.render({
            'status': 0,
            'data': welfare.jsonify(),
        })
        handle_daily_create_welfare.delay(user_id, welfare.id)
        welfare_created_notify.delay(room, welfare)
        # scheduler = TornadoScheduler()
        # scheduler.add_jobstore('redis', jobs_key='welfare:jobs', run_times_key='welfare:deadline')
        # tornado_scheduler.add_jobstore('redis', jobs_key='welfare:jobs', run_times_key='welfare:deadline')
        tornado_scheduler.add_job(welfare_end_notify, 'date', run_date=welfare.deadline, args=[welfare])

        return

    # @check_access_token
    # def get(self):
    #     try:
    #         user_id = self.get_argument('user_id')
    #         welfare_id = self.get_argument('welfare_id')
    #     except MissingArgumentError:
    #         return self.error(MISSING_PARAMS)
    #
    #     welfare_order = WelfareOrder.get_by_welfare_and_user(welfare_id, user_id)
    #     data = {
    #         'id': welfare_order.id,
    #         'user_id': welfare_order.user_id,
    #         'welfare_id': welfare_order.id,
    #         'status': welfare_order.status,
    #         'create_time': welfare_order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
    #         'delivery_time': welfare_order.delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
    #         'confirm_time': welfare_order.delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
    #     }
    #
    #     return self.render({
    #         'status': 0,
    #         'data': data,
    #     })


class WelfareRobHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            welfare_id = self.get_argument('welfare_id')
            address_id = self.get_argument('address_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        welfare = Welfare.get(welfare_id)
        if not welfare:
            return self.error(WELFARE_NOT_FOUND)

        if WelfareOrder.has_robed(welfare_id, user_id):
            return self.error(WELFARE_HAS_ROBED)

        if WelfareOrder.get_robers_count(welfare_id) == welfare.count:
            return self.error(WELFARE_HAS_ROBED_OVER)

        try:
            WelfareOrder.add(user_id, welfare_id, address_id)
            handle_daily_rob_welfare.delay(user_id, welfare_id)
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'抢福利失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class WelfareRobListHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = int(self.get_argument('user_id'))
            welfare_id = self.get_argument('welfare_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        welfare_orders = WelfareOrder.get_list_user_and_welfare(user_id, welfare_id, start, count)
        data = []
        for welfare_order in welfare_orders:
            rob_user_id = welfare_order.user_id
            user = User.get(rob_user_id)
            rst = {
                'user': {
                    'id': user.id,
                    'name': user.user_name,
                    'avatar': user.avatar_url,
                },
                'create_time': welfare_order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'delivery_time': welfare_order.delivery_time,
                'status': welfare_order.status,
            }
            if int(user.id) == user_id:
                rst['is_me'] = True
                data.insert(0, rst)
            else:
                data.append(rst)

        return self.render({
            'status': 0,
            'data': data,
        })


class WelfareRobConfirmHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            welfare_id = self.get_argument('welfare_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        welfare = Welfare.get(welfare_id)
        user = User.get(user_id)
        welfare_order = WelfareOrder.get_by_welfare_and_user(welfare_id, user_id)
        try:
            welfare_order.confirm()
            tornado_scheduler.remove_job('welfare_order_%s' % welfare_order.id)
        except Exception as e:
            logger.error(u'确认福利收货失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        welfare_confirm_notify.delay(welfare, user)
        return self.render({
            'status': 0,
        })


class WelfareDeliveryHandler(APIBaseHandler):

    def post(self):
        try:
            welfare_id = self.get_argument('welfare_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        welfare = Welfare.get(welfare_id)
        if welfare.status == WELFARE_ROB_UNDER_WAY:
            return self.error(WELFARE_UNDER_WAY)
        elif welfare.status == WELFARE_ROB_END_AND_DELIVERY:
            return self.error(WELFARE_HAS_ALREADY_DELIVERY)
        else:
            welfare.welfare_delivery()
            self.render({
                'status': 0,
            })

            # welfare_ordered_notify.delay(welfare)
            # welfare_orders = WelfareOrder.gets_by_welfare(welfare.id)
            # for welfare_order in welfare_orders:
            #     run_time = datetime.now() + timedelta(days=10)
            #     tornado_scheduler.add_job(welfare_auto_complete, 'date', id="welfare_order_%s" % welfare_order.id,
            #         run_date=run_time, args=[welfare_order])

            return


class WelfareOrderDeliveryHandler(APIBaseHandler):

    def post(self):
        try:
            welfare_id = self.get_argument('welfare_id')
            welfare_order_id = self.get_argument('welfare_order_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        welfare = Welfare.get(welfare_id)
        welfare_order = WelfareOrder.get(welfare_order_id)
        if welfare.status != WELFARE_ROB_END_AND_DELIVERY:
            return self.error(WELFARE_UNDER_WAY)

        # if welfare_order.status == 'D':
        #     return self.error(WELFARE_HAS_ALREADY_DELIVERY)
        #
        # if welfare_order.status == 'C':
        #     return self.error(WELFARE_HAS_ALREADY_COMPLETE)

        # welfare_order.delivery()
        self.render({
            'status': 0
        })
        welfare_ordered_notify.delay(welfare, welfare_order)
        run_time = datetime.now() + timedelta(days=10)
        tornado_scheduler.add_job(welfare_auto_complete, 'date', id="welfare_order_%s" % welfare_order.id,
            run_date=run_time, args=[welfare_order]
        )
        return

