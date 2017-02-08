# coding: utf-8

import time
import hashlib
from datetime import datetime
import json
from base64 import b64encode, urlsafe_b64decode
from qiniu import Auth, put_data
from hashlib import sha1
import hmac
from datetime import datetime, timedelta
from starmachine.lib.utils import get_int_date, createNoncestr
from starmachine import settings

class QiNiuStore(object):

    def __init__(self):
        self.access_key = 'AUV20tuE-G41IHIu04wZZPXxlJzaNnGNtYdeJeyM'
        self.secret_key = 'Dw4Hscr74R_Qn_KXV5M3sxDsiMM-DYnkZx78j-hz'
        self.bucket = settings.BUCKET
        self.q = Auth(self.access_key, self.secret_key)

    def init_image_key(self, file_format):
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        img_dir = 'images/%s/%s/%s/' % (year, month, day)
        random_str = '%s%s' % (int(time.time()), createNoncestr())
        m = hashlib.md5(random_str)
        file_name = m.hexdigest()
        key = '%s%s.%s' % (img_dir, file_name, file_format)
        return key

    def upload_data(self, token, key, data):
        return put_data(token, key, data)