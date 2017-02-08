# coding: utf-8

import time
import urllib
from datetime import datetime, timedelta
from tornado.web import MissingArgumentError
from starmachine.handlers.base import APIBaseHandler, BaseHandler
from starmachine.lib.utils import check_access_token
from starmachine.handlers.error import MISSING_PARAMS
from starmachine.lib.qiniu_store import QiNiuStore
from starmachine import settings


class PicPageHandler(BaseHandler):

    def get(self):
        q = QiNiuStore()
        params = {
            'user_id': '$(x:user_id)',
            'name': '$(fname)',
            'hash': '$(etag)',
            'key': '$(key)',
            'upload_status': '$(x:upload_status)',
            'room_id': '$(x:room_id)',
            'posts_id': '$(x:posts_id)',
        }
        callback_body_str = ''
        for key, val in params.items():
            callback_body_str += "%s=%s&" % (key, val)
        callback_body_str = callback_body_str[:-1]

        policy = {
            'scope': "star428",
            # 'callbackUrl': 'http://123.57.46.53:8000/api/qiniu/notify/',
            # 'callbackBody': callback_body_str,
            # 'callbackFetchKey': 1
        }
        token = q.q.upload_token('star428', policy=policy)
        self.render('pic.html', token=token)

class QiNiuTokenHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        q = QiNiuStore()
        params = {
            'user_id': '$(x:user_id)',
            'name': '$(fname)',
            'hash': '$(etag)',
            'key': '$(key)',
            'upload_status': '$(x:upload_status)',
            'room_id': '$(x:room_id)',
            'posts_id': '$(x:posts_id)',
        }
        callback_body = ''
        for key, val in params.items():
            callback_body += "%s=%s&" % (key, val)
        callback_body = callback_body[:-1]
        token = q.q.upload_token(q.bucket)
        return self.render({
            'status': 0,
            'data': {
                'token': token,
            }
        })


class QiNiuNotifyHandler(APIBaseHandler):

    def post(self):
        q = QiNiuStore()
        upload_status = self.get_argument('upload_status')
        # user_id = self.get_argument('user_id', '')
        # room_id = self.get_argument('room_id', '')
        # content_id = self.get_argument('content_id', '')
        # type = self.get_argument('type')
        file_name = self.get_argument('name')
        file_format = file_name.split('.').pop().lower()
        key = q.init_image_key(file_format)
        # if type == 'add':
        #     if upload_status == 1: # user
        #         # user = User.get(user_id):
        rst = {
            'key': key,
            'payload': {
                'name': key,
                'success': True
            }
        }
        return self.render(rst)





