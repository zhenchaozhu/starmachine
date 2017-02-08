# coding: utf-8

import urllib
import hmac
import binascii
import hashlib
from starmachine import settings

# search_host = 'http://intranet.opensearch-cn-beijing.aliyuncs.com'
# access_key_id = 'YzBTtLFnfnrUnh8z'
# access_secret = 'YSjwEy8Ged6oV6uMy41SjaobCxvFVq'
# index = settings.OPEN_SEARCH_INDEX

search_host = 'http://opensearch-cn-beijing.aliyuncs.com/search'
access_key_id = 'YzBTtLFnfnrUnh8z'
access_secret = 'YSjwEy8Ged6oV6uMy41SjaobCxvFVq'
index = settings.OPEN_SEARCH_INDEX


def format_parametr(parameter):
    """格式化参数，签名过程需要使用"""
    filter_keys = parameter.keys()
    filter_keys.sort()
    joined_string = '&'.join(['%s=%s' % (key, urllib.quote(parameter[key])) for key in filter_keys])
    return joined_string

def encrypt_sign(str):
    if isinstance(str, unicode):
        str = str.encode('utf-8')

    hash = hmac.new(access_secret + '&', str, hashlib.sha1)
    return binascii.b2a_base64(hash.digest())[:-1]