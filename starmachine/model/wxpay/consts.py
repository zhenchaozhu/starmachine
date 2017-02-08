# coding: utf-8

import os

appId = ''
appSecret = ''
paySignKey = ''
partnerId = '1219176801'
partnerKey = 'c3a7561d49c76a2aec1ead05b7927cf3'
dir = os.path.dirname(__file__)
REFUND_PEM_PATH = os.path.join(dir, 'tenpay_refund.pem')

DELIVER_NOTIFY_URL = 'https://api.weixin.qq.com/pay/delivernotify'
ORDER_QUERY_URL = 'https://api.weixin.qq.com/pay/genprepay'
ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
NOTIFY_DATA_DB_KEY = '/tencourt/wxpay/notify/data'

WEIXIN_SERVICE_TOKEN = 'wx35253c41539eeadettld'
