# coding: utf-8

import logging
import requests
from starmachine.handlers.base import APIBaseHandler
from starmachine.model.order.trade import Trade
from starmachine.model.order.trade_pay_notify import TradePayNotify
from starmachine.model.wxpay import config
from starmachine.model.wxpay import WxServer
from starmachine.model.consts import STATUS_PENDING

logger = logging.getLogger(__name__)

class WxPayNotifyAPI(APIBaseHandler):

    def post(self):
        data = self.request.body
        wx_server = WxServer()
        wx_server.saveData(data)
        data = wx_server.getData()
        if data.get('return_code') == 'SUCCESS':
            if wx_server.checkSign():
                trade_id = data.get('out_trade_no')
                trade = Trade.get(trade_id)
                if trade:
                    if trade.status == STATUS_PENDING:
                        trade.receive_pay()
                        TradePayNotify.add(trade_id, trade.pay_method, self.request.body)
                    wx_server.setReturnParameter('return_code', 'SUCCESS')
                    wx_server.setReturnParameter('return_msg', 'OK')
                    return self.render(wx_server.createXml())
                else:
                    logger.error(u'微信支付确认失败。Trade:[%s]交易ID不存在。' % trade_id)
            else:
                logger.error(u'微信支付确认失败。sign校验失败。')
        else:
            error_msg = data.get('return_msg')
            logger.error(u'微信支付确认失败。ErrorMsg:[%s]' % error_msg)

        return self.render('FAILED')



