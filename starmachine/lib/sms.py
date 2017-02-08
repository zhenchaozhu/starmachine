# coding: utf-8

import urllib
import httplib

#api_key
api_key = "4d15b87ff1852eb65718eb3c1f17f6d8"
#服务地址
host = "yunpian.com"
#端口号
port = 80
#版本号
version = "v1"
#查账户信息的URI
user_get_uri = "/" + version + "/user/get.json"
#通用短信接口的URI
sms_send_uri = "/" + version + "/sms/send.json"
#模板短信接口的URI
sms_tpl_send_uri = "/" + version + "/sms/tpl_send.json"

def send_sms(phone, content):
    """
    能用接口发短信
    """
    params = urllib.urlencode({'apikey': api_key, 'text': content, 'mobile': phone})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=port, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    try:
        print response_str
        return response_str
    except Exception as e:
        print e
        return False