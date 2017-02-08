# coding: utf-8

import json
import time
import urllib
import requests
from datetime import datetime
from rq.decorators import job
from starmachine.worker import conn
from starmachine.lib.ali_open_search import index, access_key_id, format_parametr, encrypt_sign

def handle_open_search_request(data):
    post_url = 'http://opensearch-cn-beijing.aliyuncs.com/index/doc/%s' % index
    post_params = {
        'action': 'push',
        'table_name': 'room',
        'items': json.dumps(data),
        'index_name': index,
        'AccessKeyId': access_key_id,
        'SignatureMethod': 'HMAC-SHA1',
        'Version': 'v2',
        'SignatureVersion': '1.0',
        'SignatureNonce': str(time.time()),
        'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    format_para = format_parametr(post_params)
    string_to_sign = 'POST&%s&%s' % (urllib.quote_plus('/'), urllib.quote_plus(format_para))
    sign = encrypt_sign(string_to_sign)
    post_params['Signature'] = sign
    rest = requests.post(post_url, post_params)
    print rest

@job('default', connection=conn)
def add_open_search_room(room_id, name, intro, create_time, tag_ids):
    from starmachine.model.tag import Tag
    tags = [Tag.get(tag_id).name for tag_id in tag_ids]
    data = [{
        'cmd': 'add',
        'fields': {
            'id': room_id,
            'name': name,
            'intro': intro,
            'create_time': int(time.mktime(create_time.timetuple())),
            'tags': tags,
        }
    }]
    handle_open_search_request(data)

@job('default', connection=conn)
def update_open_search_room(room_id, name, intro, tag_ids):
    from starmachine.model.tag import Tag
    tags = [Tag.get(tag_id).name for tag_id in tag_ids]
    data = [{
        'cmd': 'update',
        'fields': {
            'id': room_id,
            'name': name,
            'intro': intro,
            'tags': tags,
        }
    }]
    handle_open_search_request(data)

@job('default', connection=conn)
def delete_open_search_room(room_id):
    data = [{
        'cmd': 'update',
        'fields': {
            'id': room_id,
        }
    }]
    handle_open_search_request(data)