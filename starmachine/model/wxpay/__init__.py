# coding: utf-8

import time
import random
import logging
import urllib2
import hashlib
from tornado.httpclient import AsyncHTTPClient
from starmachine.model.consts import ORDER_CHARGE, ORDER_REWARD, ORDER_ROOM
from starmachine import settings
import xml.etree.ElementTree as ET

config = {
    'partner_id': '1241088302',
    'app_id': 'wx8902b826ec3821b4',
    'app_secret': 'f330e24244142ff4e8d9dd6f643812aa',
    'app_key': 'e01z25xmcd1gaiwz82bkggm43hhpq0sk'
}

BODY_STR = {
    ORDER_CHARGE: u'充值',
    ORDER_REWARD: u'打赏',
    ORDER_ROOM: u'房费',
}

logger = logging.getLogger(__name__)

class UrllibClient(object):
    """使用urlib2发送请求"""

    def postXml(self, xml, url, second=30):
        """不使用证书"""
        data = urllib2.urlopen(url, xml, timeout=second).read()
        return data


class CommonUtil(object):

    def trim_string(self, value):
        if value is not None and len(value) == 0:
            return None

        return value

    def get_sign(self, obj):
        """生成签名"""
        # 签名步骤一：按字典序排序参数,formatBizQueryParaMap已做
        String = self.format_parametr(obj)
        # 签名步骤二：在string后加入KEY
        String = "%s&key=%s" % (String, config.get('app_key'))
        # 签名步骤三：MD5加密
        String = hashlib.md5(String.encode('utf-8')).hexdigest()
        #签名步骤四：所有字符转为大写
        result_ = String.upper()
        return result_

    def format_parametr(self, parameter):
        """格式化参数，签名过程需要使用"""
        filter_parameter = self.para_filter(parameter)
        filter_keys = filter_parameter.keys()
        filter_keys.sort()
        joined_string = '&'.join(['%s=%s' % (key.lower(), unicode(filter_parameter[key])) for key in filter_keys])
        return joined_string

    def para_filter(self, params):
        return {key: params[key]
                for key in params
                if key.lower() not in {'sign', 'sign_type'} and params[key]}

    def createNoncestr(self, length=32):
        """产生随机字符串，不长于32位"""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    def arrayToXml(self, arr):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in arr.iteritems():
            xml.append("<{0}>{1}</{0}>".format(k, unicode(v).encode('utf-8')))
        xml.append("</xml>")
        return "".join(xml)

    def xmlToArray(self, xml):
        """将xml转为array"""
        array_data = {}
        root = ET.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data


class WxUnifiedOrder(CommonUtil):

    def __init__(self, trade, remote_ip):
        self.url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        self.time_out = 30
        self.parameter = {
            'appid': config.get('app_id'),
            'mch_id': config.get('partner_id'),
            'nonce_str': self.createNoncestr(),
            'body': BODY_STR.get(int(trade.order_type)),
            'out_trade_no': str(trade.id),
            'total_fee': int(trade.amount * 100),
            'spbill_create_ip': remote_ip,
            'notify_url': '%s%s' % (settings.HOST, '/api/wxpay/notify/'),
            'trade_type': 'APP'
        }

    def createXML(self):
        sign = self.get_sign(self.parameter)
        self.parameter['sign'] = sign
        return self.arrayToXml(self.parameter)

    def getWxResponse(self, callback):
        """获取wx_response"""

        def on_response(response):
            xml = response.body
            callback(xml)

        xml = self.createXML()
        client = AsyncHTTPClient()
        request = self.generate_post_request(xml)
        client.fetch(request, on_response)

    def getPrepayId(self, callback):
        """获取prepay_id"""
        def on_response(response):
            xml = response.body
            self.result = self.xmlToArray(xml)
            prepay_id = self.result["prepay_id"]
            callback(prepay_id)

        xml = self.createXML()
        client = AsyncHTTPClient()
        request = self.generate_post_request(xml)
        client.fetch(request, on_response)

    def generate_post_request(url, xml, timeout=30, headers=None):
        from tornado import httpclient
        request = httpclient.HTTPRequest(
            url='https://api.mch.weixin.qq.com/pay/unifiedorder',
            body=xml,
            method='POST',
            headers=headers,
            request_timeout=timeout
        )
        return request


class WxPay(CommonUtil):

    def __init__(self, trade, remote_ip):
        self.trade = trade
        self.remote_id = remote_ip

    def get_parameters(self, callback):
        def on_response(xml):
            try:
                result = self.xmlToArray(xml)
                prepay_id = result["prepay_id"]
                params['prepayid'] = prepay_id
                sign = self.get_sign(params)
                params['sign'] = sign
                callback(params)
            except Exception as e:
                logger.error(u'请求微信数据失败。Error:[%s] Response:[%s]' % (e, xml))
                raise

        params = {
            'appid': config.get('app_id'),
            'partnerid': config.get('partner_id'),
            'package': 'Sign=WXPay',
            'noncestr': self.createNoncestr(),
            'timestamp': int(time.time()),
        }
        WxUnifiedOrder(self.trade, self.remote_id).getWxResponse(on_response)


class WxServer(CommonUtil):
    """响应型接口基类"""
    SUCCESS, FAIL = "SUCCESS", "FAIL"

    def __init__(self):
        self.data = {}  # 接收到的数据，类型为关联数组
        self.returnParameters = {}  # 返回参数，类型为关联数组

    def saveData(self, xml):
        """将微信的请求xml转换成关联数组，以方便数据处理"""
        self.data = self.xmlToArray(xml)

    def checkSign(self):
        """校验签名"""
        tmpData = dict(self.data)  # make a copy to save sign
        del tmpData['sign']
        sign = self.get_sign(tmpData)  # 本地签名
        if self.data['sign'] == sign:
            return True
        return False

    def arrayToXml(self, arr):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in arr.iteritems():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, unicode(v).encode('utf-8')))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, unicode(v).encode('utf-8')))
        xml.append("</xml>")
        print "".join(xml)
        return "".join(xml)

    def getData(self):
        """获取微信的请求数据"""
        return self.data

    def setReturnParameter(self, parameter, parameterValue):
        """设置返回微信的xml数据"""
        self.returnParameters[self.trim_string(parameter)] = self.trim_string(parameterValue)

    def createXml(self):
        """生成接口参数xml"""
        return self.arrayToXml(self.returnParameters)

    def returnXml(self):
        """将xml数据返回微信"""
        returnXml = self.createXml()
        return returnXml
