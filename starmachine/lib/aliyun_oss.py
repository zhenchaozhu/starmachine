# coding: utf-8

import time
from datetime import datetime
import hashlib
from oss.oss_api import OssAPI
from starmachine.lib.utils import createNoncestr

access_key = 'kP0RUM7qIYGA0VQz'
access_key_secret = 'NMvfqmVzHZMPuPVmrQ2Mm7Muf1OAdh'
bucket = 'starmachine'
aliyun_beijing_endpoint = 'oss-cn-beijing.aliyuncs.com'

class AliOss(object):

    def __init__(self, access_key, access_key_secret, bucket, endpoint):
        self.access_key = access_key
        self.access_key_secret = access_key_secret
        self.bucket = bucket
        self.endpoint = endpoint
        self.oss = OssAPI(endpoint, access_key, access_key_secret)

    def put_user_avatar(self, user_id, avatar):
        content_type = avatar['content_type']
        file_format = avatar['filename'].split('.').pop().lower()
        file_name = '%s_%s' % (user_id, int(time.time()))
        file_dir = 'avatar/user/%s.%s' % (file_name, file_format)
        res = self.oss.put_object_from_string(self.bucket, file_dir, avatar['body'], content_type)
        if res.status == 200:
            return file_dir

    def put_room_avatar(self, user_id, avatar):
        content_type = avatar['content_type']
        file_format = avatar['filename'].split('.').pop().lower()
        file_name = '%s_%s' % (user_id, int(time.time()))
        file_dir = 'avatar/room/%s.%s' % (file_name, file_format)
        res = self.oss.put_object_from_string(self.bucket, file_dir, avatar['body'], content_type)
        if res.status == 200:
            return file_dir

    def put_validate(self, user_id, validate):
        content_type = validate['content_type']
        file_format = validate['filename'].split('.').pop().lower()
        file_name = '%s_%s%s' % (user_id, int(time.time()), createNoncestr())
        m = hashlib.md5()
        m.update(file_name)
        file_name = m.hexdigest()
        file_dir = 'validate/%s.%s' % (file_name, file_format)
        res = self.oss.put_object_from_string(self.bucket, file_dir, validate['body'], content_type)
        if res.status == 200:
            return file_dir

    def put_images(self, user_id, files):
        file_dirs = []
        now = datetime.now()
        date_str = now.strftime('%Y%m%d_%H')
        img_dir = 'images/%s/' % date_str
        for file in files:
            file_name = file['filename']
            content_type = file['content_type']
            file_format = file['filename'].split('.').pop().lower()
            hash_str = '%s%s%s' % (int(time.time()), user_id, file_name)
            m = hashlib.md5()
            m.update(hash_str)
            m_digest = m.hexdigest()
            md5_file_name = '%s.%s' % (m_digest, file_format)
            object_path = img_dir + md5_file_name
            res = self.oss.put_object_from_string(self.bucket, object_path, file['body'], content_type)
            if res.status == 200:
                file_dirs.append(object_path)

        return file_dirs

    def put_video(self, user_id, video):
        content_type = video['content_type']
        file_format = video['filename'].split('.').pop().lower()
        file_name = '%s_%s' % (user_id, int(time.time()))
        file_dir = 'video/%s.%s' % (file_name, file_format)
        res = self.oss.put_object_from_string(self.bucket, file_name, video['body'], content_type)
        if res.status == 200:
            return file_dir

beijing_ali_oss = AliOss(access_key, access_key_secret, bucket, aliyun_beijing_endpoint)