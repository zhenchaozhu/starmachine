# coding: utf-8

import json
import logging
from tornado.web import MissingArgumentError
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token, encrypt_password
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, CONTENT_NOT_FOUND, SYSTEM_ERROR, \
    ACCESS_NOT_ALLOWED, PAYMENT_CODE_NOT_EXISTS, PAYMENT_CODE_ERROR
from starmachine.model.user import User, UserPaymentCode
from starmachine.model.content import Content
from starmachine.model.order.reward_order import RewardOrder

logger = logging.getLogger(__name__)

class RewardHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            receiver_id = self.get_argument('receiver_id')
            content_id = self.get_argument('content_id')
            trades_info = self.get_argument('trades_info')
            room_id = self.get_argument('room_id')
            amount = self.get_argument('amount')
            payment_code = self.get_argument('payment_code')
            trades_info = json.loads(trades_info)
        except (MissingArgumentError, TypeError):
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        user_payment_code = UserPaymentCode.get_by_user(user_id)
        if not user_payment_code:
            return self.error(PAYMENT_CODE_NOT_EXISTS)

        payment_code = encrypt_password(payment_code)
        if payment_code != str(user_payment_code.payment_code):
            return self.error(PAYMENT_CODE_ERROR)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        if int(content.room_id) != int(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            reward_order = RewardOrder.add(user_id, receiver_id, content_id, room_id, amount, trades_info)
        except Exception as e:
            logger.error(u'生成打赏订单失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': reward_order.jsonify()
        })

