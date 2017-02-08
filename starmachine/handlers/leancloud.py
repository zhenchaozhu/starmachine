# coding: utf-8

import json
import time
import random
import hmac, hashlib
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import ACCESS_NOT_ALLOWED
from starmachine.lib.utils import check_access_token
from starmachine.model.friendship import UserFollows

app_id = 'q70mf6jpnlscrbmlrxg9oyp7kis9jzg2eoq87fabz3ii0vom'
app_key = 'x5564r3expohn6mon2k00lkp7kcji2yhg7vghf45a42bp7um'
app_secret = 'c10nwba1z953cfrgiu6wnjj5kq09sb1f2avvc1v1iti7iyfg'

def getNonce(length=5):
    d = []
    for i in range(0, length):
        d.append(str(random.randint(1, 9)))
    return ''.join(d)

def sign(msg, k):
    return hmac.new(k, msg, hashlib.sha1).digest().encode('hex')

class LeanCloudSignHandler(APIBaseHandler):

    def post(self):
        data = json.loads(self.request.body)
        user_id = data.get('clientId')
        member_ids = data.get('members')
        conv_id = data.get('convId')
        action = data.get('action')
        timestamp = int(time.time())
        nonce = getNonce(5)
        if not member_ids:
            msg = '%s:%s::%s:%s' % (app_id, user_id, timestamp, nonce)
        else:
            member_ids.sort()
            member_ids = ':'.join(member_ids)
            if not conv_id:
                msg = '%s:%s:%s:%s:%s' % (app_id, user_id, member_ids, timestamp, nonce)
            else:
                msg = '%s:%s:%s:%s:%s:%s:%s' % (app_id, user_id, conv_id, member_ids, timestamp, nonce, action)

        signature = sign(msg, app_secret)
        return self.render({
            'nonce': nonce,
            'timestamp': timestamp,
            'signature': signature,
        })


class LeanCloudPeerChatHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        chat_user_id = self.get_argument('chat_user_id')

        if not UserFollows.follow_each_other(user_id, chat_user_id):
            return self.error(ACCESS_NOT_ALLOWED)







