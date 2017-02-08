# coding: utf-8

import time
import json
import urllib2
import logging
from starmachine.lib.utils import md5
from starmachine import settings

android_app_key = '5501362bfd98c5b68e00026c'
android_app_master_secret = 'w5tpsm6xjvqabdyeggyhv3kiuosisnjo'
host = 'http://msg.umeng.com/api/send'
logger = logging.getLogger(__name__)
ios_app_key = '55c95d3ee0f55ab67a007beb'
ios_app_master_secret = '2uynyywvts4vaeyusatehr6he1u5ra9e'
if not settings.DEBUG:
    production_mode = 'true'
else:
    production_mode = 'false'


class AndroidPayload(object):

    def __init__(self, display_type='notification', ticker=None, title=None, text=None, icon=None, largeIcon=None,
        img=None, sound=None, builder_id=None, play_vibrate=None, play_lights=None, play_sound=None,
        after_open="go_custom", url=None, activity=None, custom=None, extra=None):
            super(AndroidPayload, self).__init__()
            self.display_type = display_type
            self.ticker = ticker
            self.title = title
            self.text = text
            self.icon = icon
            self.largeIcon = largeIcon
            self.img = img
            self.sound = sound
            self.builder_id = builder_id
            self.play_vibrate = play_vibrate
            self.play_lights = play_lights
            self.play_sound = play_sound
            self.after_open = after_open
            self.url = url
            self.activity = activity
            self.custom = custom
            self.extra = extra

    def dict(self):
        payload = {}
        payload['display_type'] = 'notification'
        body = {}
        body['ticker'] = self.ticker
        body['title'] = self.title
        body['text'] = self.text
        body['after_open'] = self.after_open
        if self.icon:
            body['icon'] = self.icon
        if self.largeIcon:
            body['largeIcon'] = self.largeIcon
        if self.img:
            body['img'] = self.img
        if self.sound:
            body['sound'] = self.sound
        if self.builder_id:
            body['builder_id'] = self.builder_id
        if self.play_vibrate:
            body['play_vibrate'] = self.play_vibrate
        if self.play_lights:
            body['play_lights'] = self.play_lights
        if self.play_sound:
            body['play_sound'] = self.sound
        if self.url:
            body['url'] = self.url
        if self.activity:
            body['activity'] = self.activity
        if self.custom:
            body['custom'] = self.custom
        payload['body'] = body
        if self.extra:
            payload['extra'] = self.extra
        return payload


class IOSPayload(object):

    def __init__(self, alert=None, badge=None, sound='default', category=None, content_available=False, extra=None):
        super(IOSPayload, self).__init__()
        self.alert = alert
        self.badge = badge
        self.sound = sound
        self.category = category
        self.content_available = content_available
        self.extra = extra

    def dict(self):
        d = {}
        if self.alert:
            d['alert'] = self.alert
        if self.sound:
            d['sound'] = self.sound
        if self.badge is not None:
            d['badge'] = int(self.badge)
        if self.category:
            d['category'] = self.category

        if self.content_available:
            d.update({'content-available': 1})

        d = {'aps': d}
        d.update(self.extra)
        return d


class UmpnsClient(object):

    def __init__(self):
        self.host = host
        self.method = 'POST'
        self.app_key = ''
        self.app_master_secret = ''

    def init_params(self, type=None, device_tokens=None, payload=None, alias_type=None,
                    alias=None, field_id=None, filter=None, start_time=None, expire_time=None, max_send_num=None,
                    out_biz_no=None, production_mode=None, description=None, thirdparty_id=None):
        timestamp = int(time.time() * 1000)
        policy = {}
        if start_time:
            policy['start_time'] = start_time
        if expire_time:
            policy['expire_time'] = expire_time
        if max_send_num:
            policy['max_send_num'] = max_send_num
        if out_biz_no:
            policy['out_biz_no'] = out_biz_no

        params = {
            'appkey': self.app_key,
            'timestamp': timestamp,
            'type': type,
            'payload': payload,
        }

        if device_tokens:
            params['device_tokens'] = device_tokens
        if policy:
            params['policy'] = policy
        if alias_type:
            params['alias_type'] = alias_type
        if alias:
            params['alias'] = alias
        if field_id:
            params['field_id'] = field_id
        if filter:
            params['filter'] = filter
        if production_mode:
            params['production_mode'] = production_mode
        if description:
            params['description'] = description
        if thirdparty_id:
            params['thirdparty_id'] = thirdparty_id

        return params

class AndroidPushClient(UmpnsClient):

    def __init__(self):
        super(AndroidPushClient, self).__init__()
        self.app_key = android_app_key
        self.app_master_secret = android_app_master_secret

    def push_unicast(self, device_token, ticker, title, text, custom=None, **kwargs):
        payload = AndroidPayload(ticker=ticker, title=title, text=text, custom=custom).dict()
        post_params = self.init_params(type='unicast', device_tokens=device_token, payload=payload, **kwargs)
        post_body = json.dumps(post_params)
        sign = md5('%s%s%s%s' % (self.method, self.host, post_body, self.app_master_secret))
        try:
            r = urllib2.urlopen(self.host + '?sign=' + sign, data=post_body)
            rst = json.loads(r.read())
            if rst.get('ret') == 'SUCCESS':
                return True
            else:
                logger.warning(u'推送失败。Rest:[%s]' % rst.data)
                raise PushNotifyException
        except (urllib2.HTTPError, urllib2.URLError), e:
            logger.error(u'推送失败。Error:[%s]' % e)
            raise PushNotifyException

    def push_listcast(self, device_tokens, ticker, title, text, custom=None, **kwargs):
        payload = AndroidPayload(ticker=ticker, title=title, text=text, custom=custom).dict()
        post_params = self.init_params(type='listcast', device_tokens=device_tokens, payload=payload, **kwargs)
        post_body = json.dumps(post_params)
        sign = md5('%s%s%s%s' % (self.method, self.host, post_body, self.app_master_secret))
        try:
            r = urllib2.urlopen(self.host + '?sign=' + sign, data=post_body)
            rst = json.loads(r.read())
            if rst.get('ret') == 'SUCCESS':
                return True
            else:
                logger.warning(u'推送失败。Rest:[%s]' % rst.data)
                raise PushNotifyException
        except (urllib2.HTTPError, urllib2.URLError), e:
            logger.error(u'推送失败。Error:[%s]' % e)
            raise PushNotifyException


class IOSPushClient(UmpnsClient):

    def __init__(self):
        super(IOSPushClient, self).__init__()
        self.app_key = ios_app_key
        self.app_master_secret = ios_app_master_secret

    def push_unicast(self, device_token, alert, extra=None, **kwargs):
        payload = IOSPayload(alert=alert, extra=extra).dict()
        post_params = self.init_params(type='unicast', device_tokens=device_token, payload=payload, production_mode=production_mode, **kwargs)
        post_body = json.dumps(post_params)
        sign = md5('%s%s%s%s' % (self.method, self.host, post_body, self.app_master_secret))
        try:
            r = urllib2.urlopen(self.host + '?sign=' + sign, data=post_body)
            rst = json.loads(r.read())
            if rst.get('ret') == 'SUCCESS':
                return True
            else:
                logger.warning(u'推送失败。Rest:[%s]' % rst.data)
                raise PushNotifyException
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e.read()
            logger.error(u'推送失败。Error:[%s]' % e)
            raise PushNotifyException

    def push_listcast(self, device_tokens, alert, extra, **kwargs):
        payload = IOSPayload(alert=alert, extra=extra).dict()
        post_params = self.init_params(type='listcast', device_tokens=device_tokens, payload=payload, production_mode=production_mode, **kwargs)
        post_body = json.dumps(post_params)
        sign = md5('%s%s%s%s' % (self.method, self.host, post_body, self.app_master_secret))
        try:
            r = urllib2.urlopen(self.host + '?sign=' + sign, data=post_body)
            rst = json.loads(r.read())
            if rst.get('ret') == 'SUCCESS':
                return True
            else:
                logger.warning(u'推送失败。Rest:[%s]' % rst.data)
                raise PushNotifyException
        except (urllib2.HTTPError, urllib2.URLError), e:
            logger.error(u'推送失败。Error:[%s]' % e)
            raise PushNotifyException

    def get_file_id(self, device_tokens):
        post_url = 'http://msg.umeng.com/upload'
        timestamp = int(time.time() * 1000)
        validationToken = md5(self.app_key.lower() + self.app_master_secret.lower() + str(timestamp))
        post_content = {
            'appkey': self.app_key,
            'timestamp': timestamp,
            'validation_token': validationToken,
            'content': device_tokens
        }
        post_body = json.dumps(post_content)
        rst = urllib2.urlopen(post_url, data=post_body)
        rst = json.loads(rst.read())
        file_id = rst.get('data').get('file_id')
        return file_id

    def push_filecast(self, device_tokens, alert, extra):
        file_id = self.get_file_id(device_tokens)
        payload = IOSPayload(alert=alert, extra=extra).dict()
        post_params = self.init_params(type='filecast', production_mode=production_mode,  payload=payload)
        post_params['file_id'] = file_id
        post_body = json.dumps(post_params)
        sign = md5('%s%s%s%s' % (self.method, self.host, post_body, self.app_master_secret))
        try:
            r = urllib2.urlopen(self.host + '?sign=' + sign, data=post_body)
            rst = json.loads(r.read())
            if rst.get('ret') == 'SUCCESS':
                return True
            else:
                logger.warning(u'推送失败。Rest:[%s]' % rst.data)
                raise PushNotifyException
        except (urllib2.HTTPError, urllib2.URLError), e:
            logger.error(u'推送失败。Error:[%s]' % e)
            raise PushNotifyException

class PushNotifyException(Exception):
    pass

um_ios_client = IOSPushClient()
um_android_client = AndroidPushClient()