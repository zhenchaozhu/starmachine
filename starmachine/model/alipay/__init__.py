# encoding: utf-8

import urllib
import base64
import hashlib
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from starmachine.model.consts import ORDER_REWARD, ORDER_CHARGE, ORDER_ROOM
from starmachine.model.alipay.consts import ALIPAY_PUBLIC_KEY, BUSINESS_PRIVATE_KEY
from starmachine import settings

BODY_STR = {
    ORDER_CHARGE: u'充值',
    ORDER_REWARD: u'打赏',
    ORDER_ROOM: u'房费',
}

config = {
    'partner_id': '2088912416973116',
    'secret_key': 'z5m6tl52y3i59tnq1hduldwh7fl3b5aq',
    'input_charset': 'utf-8',
    'seller_email': 'develop@star428.com',
    'sign_type': 'RSA'
}

def filter_para(paras):
    """过滤空值和签名"""
    for k, v in paras.items():
        if not v or k in ['sign', 'sign_type']:
            paras.pop(k)
    return paras

def create_link_string(paras, sort, encode):
    """对参数排序并拼接成query string的形式"""
    if sort:
        paras = sorted(paras.items(), key=lambda d:d[0])
    if encode:
        return urllib.urlencode(paras)
    else:
        if not isinstance(paras, list):
            paras = list(paras.items())
        ps = ''
        for p in paras:
            if ps:
                ps = '%s&%s=%s' % (ps, p[0], ''.join(p[1]))
            else:
                ps = '%s=%s' % (p[0], ''.join(p[1]))
        return ps

def format_parametr(parameter):
    """格式化参数，签名过程需要使用"""
    filter_parameter = para_filter(parameter)
    filter_keys = filter_parameter.keys()
    filter_keys.sort()
    joined_string = '&'.join(['%s=%s' % (key.lower(), filter_parameter[key]) for key in filter_keys])
    return joined_string

def para_filter(params):
    return {key: params[key]
            for key in params
            if key.lower() not in {'sign', 'sign_type'} and params[key]}

def rsa_sign(para_str):
    """对请求参数做rsa签名"""
    key = RSA.importKey(BUSINESS_PRIVATE_KEY)
    h = SHA.new(para_str.encode('utf-8'))
    signer = PKCS1_v1_5.new(key)
    return urllib.quote(base64.b64encode(signer.sign(h)))

def rsa_verify(paras, sign):
    """对签名做rsa验证"""
    pub_key = RSA.importKey(ALIPAY_PUBLIC_KEY)
    paras = filter_para(paras)
    paras = create_link_string(paras, True, False)
    verifier = PKCS1_v1_5.new(pub_key)
    data = SHA.new(paras)
    return verifier.verify(data, base64.b64decode(sign))

def md5_verify(paras, sign):
    """对签名做md5验证"""
    paras = filter_para(paras)
    paras = create_link_string(paras, True, False)
    return md5_sign(paras) == sign

def md5_sign(para):
    return hashlib.md5('%s%s' % (para, config.get('secret_key'))).hexdigest()

def build_mobile_securitypay_request(trade):
    partner = config.get('partner_id')
    seller_id = config.get('seller_email')
    out_trade_no = trade.id
    subject = BODY_STR.get(trade.order_type)
    body = BODY_STR.get(trade.order_type)
    total_fee = float(trade.amount)
    notify_url = '%s%s' % (settings.HOST, '/api/alipay/notify/')
    service = 'mobile.securitypay.pay'
    payment_type = 1
    _input_charset = 'utf-8'

    orderInfo = 'partner="%s"&seller_id="%s"&out_trade_no="%s"&subject="%s"&body="%s"&total_fee="%s"&notify_url="%s"' \
        '&service="%s"&payment_type="%s"&_input_charset="%s"' % (partner, seller_id, out_trade_no, subject, body,
        total_fee, notify_url, service, payment_type, _input_charset)
    sign = rsa_sign(orderInfo)
    sign_type = config.get('sign_type')
    return orderInfo + '&sign="%s"&sign_type="%s"' % (sign, sign_type)

def build_trans_notify_url(detail_data, batch_no, batch_num, batch_fee, create_time):
    trans_notify_gateway = 'https://mapi.alipay.com/gateway.do?'
    parameter = {
        'service': 'batch_trans_notify',
        'partner': config.get('partner_id'),
        '_input_charset': 'utf-8',
        'notify_url': '%s%s' % (settings.HOST, '/api/wallet/withdraw/notify/'),
        'account_name': u'北京夸克时代科技有限公司'.encode('utf-8'),
        'detail_data': detail_data.encode('utf-8'),
        'batch_no': batch_no,
        'batch_num': batch_num,
        'batch_fee': batch_fee,
        'email': config.get('seller_email'),
        'pay_date': create_time.strftime('%Y%m%d'),
    }
    params = create_link_string(parameter, True, False)
    sign_str = md5_sign(params)
    parameter['sign'] = sign_str
    parameter['sign_type'] = 'MD5'
    encode_parameter = urllib.urlencode(parameter)
    return trans_notify_gateway + encode_parameter
