# coding: utf-8

import logging
from tornado import web
import urllib
from starmachine.handlers.base import APIBaseHandler, BaseHandler
from starmachine.model.order.trade import Trade
from starmachine.model.order.trade_pay_notify import TradePayNotify
from starmachine.model.alipay import rsa_verify, config, md5_verify
from starmachine.model.consts import STATUS_PENDING, PAYMETHOD_ALIPAY
from starmachine.model.withdraw import WithdrawBatch

logger = logging.getLogger(__name__)


def check_notify_id(notify_id):
    params = {
        'service': 'notify_verify',
        'partner': config.get('partner_id'),
        'notify_id': notify_id
    }
    query = '&'.join('='.join([str(k), str(v)])
                     for k, v in params.iteritems())
    verify_url = '%s%s' % ('https://mapi.alipay.com/gateway.do?', query)
    res = urllib.urlopen(verify_url).read()

    return str(res) == 'true'


class AlipayNotifyHandler(BaseHandler):

    def post(self):
        # 基本参数
        notify_id = self.get_argument('notify_id')
        notify_time = self.get_argument('notify_time')
        notify_type = self.get_argument('notify_type')
        sign_type = self.get_argument('sign_type')
        sign = self.get_argument('sign')

        # 业务参数
        out_trade_no = self.get_argument('out_trade_no')
        trade_status = self.get_argument('trade_status')

        params = self.request.arguments
        if not rsa_verify(params, sign):
            raise web.HTTPError(400)

        if not check_notify_id(notify_id):
            raise web.HTTPError(400)

        if trade_status in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
            trade = Trade.get(out_trade_no)
            if not trade:
                raise web.HTTPError(400)
            if trade:
                if trade.status == STATUS_PENDING:
                    trade.receive_pay()
                    TradePayNotify.add(out_trade_no, PAYMETHOD_ALIPAY, self.request.body)

            return self.finish('success')

        raise web.HTTPError(400)


class AlipayTransNotifyHandler(BaseHandler):

    def post(self):
        notify_id = self.get_argument('notify_id')
        batch_no = self.get_argument('batch_no')
        sign = self.get_argument('sign')
        success_details = self.get_argument('success_details', '')
        fail_details = self.get_argument('fail_details', '')
        params = self.request.arguments

        if not check_notify_id(notify_id):
            raise web.HTTPError(400)

        if not md5_verify(params, sign):
            raise web.HTTPError(400)

        batch = WithdrawBatch.get(batch_no)
        if not batch:
            raise web.HTTPError(400)

        if batch:
            if batch.status == STATUS_PENDING:
                batch.handle_trans(success_details, fail_details)

            return self.finish('success')

        raise web.HTTPError(400)




