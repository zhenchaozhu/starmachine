# coding: utf-8

import os
import json
import unittest
import logging
from starmachine import settings

from rong import ApiClient
#您应该将key 和 secret 保存在服务器的环境变量中
os.environ.setdefault('rongcloud_app_key', settings.RONGCLOUD_APP_KEY)
os.environ.setdefault('rongcloud_app_secret', settings.RONGCLOUD_APP_SECRET)

logging.basicConfig(level=logging.INFO)

rong_client = ApiClient(settings.RONGCLOUD_APP_KEY, settings.RONGCLOUD_APP_SECRET)