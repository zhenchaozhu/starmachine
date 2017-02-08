# coding: utf-8

import re
import hmac
import hashlib
import binascii
import base64
import uuid
import OpenSSL
import time
import random
from datetime import datetime
from tornado.web import MissingArgumentError
from starmachine.model.user_auth import UserAuth
from starmachine.handlers.error import INVALID_ACCESS_TOKEN, MISSING_PARAMS, INVALID_API_KEY_OR_SECRET, USER_NOT_FOUND
from starmachine.lib.redis_cache import CacheManager
from starmachine import settings


ENCRYPT_SECRET = 'BititInDifferentWayTencourt'
DEFAULT_ALPHABET = 'ZUBJA01FlhNWKmbX2DrzEpysoL7OvMcQPjV4Rn9t3gdT5xakwI6qufYGCHSei8'
APP_API_KEY = '0b07e8037029e05b2117b80a507da111'
APP_API_SECRET = '72ec644ae9c94cb2'
API_KEY = 794858960718520411
API_SECRET = 8281104087740140722
redis_cache = CacheManager().cache

def createNoncestr(length=12):
    """产生随机字符串，不长于12位"""
    chars = "0123456789"
    strs = []
    for x in xrange(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)

def init_trade_id():
    now_str = datetime.now().strftime('%Y%m%d%H%M%S')
    return now_str + createNoncestr()

def init_pic_url(short_url):
    if not short_url:
        return ''

    if settings.Profile.is_develop:
        domain = 'http://7xj2qd.com2.z0.glb.qiniucdn.com/'
    else:
        domain = settings.IMAGE_DOMAIN

    return domain + short_url

def md5(str):
    m = hashlib.md5(str)
    return m.hexdigest()

def num2string(num):
    numbers = []

    while num:
        num, remain = divmod(num, len(DEFAULT_ALPHABET))
        numbers.insert(0, DEFAULT_ALPHABET[remain])

    return ''.join(numbers)

def gen_public_key(int64_key):
    k1 = int64_key
    k2 = (3 * int64_key) & 0xffffffffffffffff
    s1 = '%016x' % k1
    s2 = '%016x' % k2
    return s1 + s2

def get_int_key(str32_key):
    if len(str32_key) == 32:
        s1 = str32_key[0:16]
        try:
            k1 = int(s1, 16)
            if k1 >= 0 and gen_public_key(k1) == str32_key:
                return k1
        except ValueError:
            return None

def get_int_date(date):
    return time.mktime(date.timetuple())

# 手机号码验证
def verify_telephone(telephone):
    phonePattern = re.compile(r'^(0|86|17951)?(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    return bool(phonePattern.match(telephone))

# 加密用户登录密码
def encrypt_password(password):
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    hash = hmac.new(ENCRYPT_SECRET, password, hashlib.sha1)
    return binascii.b2a_base64(hash.digest())[:-1]

def get_str_length(ustring):
    sum = 0
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code < 0x0020 or inside_code > 0x7e:
            sum += 2
        else:
            sum += 1

    return sum

# 根据概率获取随机数
def random_pick(seq, probability):
    x = random.uniform(0, 1)
    cumulative_probability = 0.0
    for item, item_probability in zip(seq, probability):
        cumulative_probability += item_probability
        if x < cumulative_probability: break

    return item

def gen_access_token(user_id):
    str = '%sstar%s' % (user_id, num2string(int(uuid.UUID(bytes=OpenSSL.rand.bytes(16)).get_hex(), 16)))
    return base64.encodestring(str).replace('\n', '')

def check_api_key(func):
    def wrap(self, *args, **kwargs):
        try:
            app_key = self.get_argument('app_key')
            app_secret = self.get_argument('app_secret')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if get_int_key(app_key) == API_KEY and int(app_secret, 16) == API_SECRET:
            return func(self, *args, **kwargs)

        return self.error(INVALID_API_KEY_OR_SECRET)

    return wrap

def check_access_token(func):
    def wrap(self, *args, **kwargs):
        try:
            access_token = self.get_argument('access_token')
            user_id = self.get_argument('user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)
        user_auth = UserAuth.get_by_user_id(user_id)
        if not user_auth:
            return self.error(USER_NOT_FOUND)

        if access_token != user_auth.access_token:
            return self.error(INVALID_ACCESS_TOKEN)

        return func(self, *args, **kwargs)

    return wrap

def redis_cache_obj(key):
    def deco(func):
        def wrap(self, id, *args, **kwargs):
            h_key = key % id
            value = redis_cache.hgetall(h_key)
            if not value:
                rst = func(self, id, *args, **kwargs)
                if rst:
                    _obj = rst.__dict__
                    redis_cache.hmset(h_key, _obj)

                return rst

            return self(**value)

        return wrap

    return deco

def redis_cache_amount(key):
    def deco(func):
        def wrap(self, id, date, *args, **kwargs):
            cache_key = key % (id, date)
            value = redis_cache.get(cache_key)
            if not value:
                rst = func(self, id, date, *args, **kwargs)
                redis_cache.set(cache_key, rst)
                return rst

            return value

        return wrap

    return deco