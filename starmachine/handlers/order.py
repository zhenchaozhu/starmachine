# coding: utf-8

import logging
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.web import MissingArgumentError, gen, asynchronous
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, SYSTEM_ERROR, TRADE_NOT_FOUND, \
    ACCOUNT_BALANCE_NOT_ENOUGH, ACCOUNT_NOT_FOUND, ACCOUNT_PAY_FAILED, ACCESS_NOT_ALLOWED
from starmachine.model.consts import PAYMETHOD_UNSET, ORDER_CHARGE, PAYMETHOD_WEIXIN, STATUS_PENDING, PAYMETHOD_ALIPAY
from starmachine.model.user import User
from starmachine.model.account import Account
from starmachine.model.order.charge import ChargeOrder
from starmachine.model.order.trade import Trade
from starmachine.model.wxpay import WxUnifiedOrder, WxPay
from starmachine.model.alipay import build_mobile_securitypay_request

logger = logging.getLogger(__name__)

class ChargeOrderHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            amount = self.get_argument('amount')
            pay_method = self.get_argument('pay_method')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        try:
            charge_order = ChargeOrder.add(user_id, amount, ORDER_CHARGE, pay_method)
        except Exception as e:
            logger.error(u'创建充值订单失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': charge_order.jsonify(),
        })


class AccountPayHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            trade_id = self.get_argument('trade_id')
            order_id = self.get_argument('order_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        trade = Trade.get(trade_id)
        if not trade:
            return self.error(TRADE_NOT_FOUND)

        if int(trade.order_id) != int(order_id):
            return self.error(ACCESS_NOT_ALLOWED)

        account = Account.get_by_user(user_id)
        if not account:
            return self.error(ACCOUNT_NOT_FOUND)

        if float(account.balance) < float(trade.amount):
            return self.error(ACCOUNT_BALANCE_NOT_ENOUGH)

        try:
            trade.receive_pay()
        except Exception as e:
            logger.error(u'余额支付失败。Error:[%s]' % e)
            return self.error(ACCOUNT_PAY_FAILED)
        account = Account.get_by_user(user_id)
        return self.render({
            'status': 0,
            'data': {
                'balance': float(account.balance),
            }
        })


class TradePayHandler(APIBaseHandler):

    @check_access_token
    @asynchronous
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            trade_id = self.get_argument('trade_id')
            order_id = self.get_argument('order_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        trade = Trade.get(trade_id)
        if not trade:
            return self.error(TRADE_NOT_FOUND)

        if int(trade.order_id) != int(order_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            if int(trade.pay_method) == PAYMETHOD_WEIXIN:
                WxPay(trade, self.remote_ip).get_parameters(self.wx_on_response)
            elif int(trade.pay_method) == PAYMETHOD_ALIPAY:
                alipay_request = build_mobile_securitypay_request(trade)
                return self.render({
                    'status': 0,
                    'pay_method': PAYMETHOD_ALIPAY,
                    'data': alipay_request
                })
        except Exception as e:
            logger.error(u'请求第三方支付数据失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

    def wx_on_response(self, response):
        wx_params = response
        return self.render({
            'status': 0,
            'pay_method': PAYMETHOD_WEIXIN,
            'data': wx_params
        })
