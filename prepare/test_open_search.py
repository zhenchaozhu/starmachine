#coding=utf-8

import time
from datetime import datetime
import urllib
import json
import hashlib
import requests
import json
import urllib2
from starmachine.model.tag import Tag
from starmachine.model.room import Room
from starmachine.model.room_tag import RoomTag
from starmachine.lib.ali_open_search import access_key_id, format_parametr, encrypt_sign

post_url = 'http://intranet.opensearch-cn-beijing.aliyuncs.com/index/doc/starmachine_room'
# tags = Tag.gets_all()
rooms = Room.gets_all()
# room_tags = RoomTag.gets_all()

data = []
for room in rooms:
    tags = RoomTag.get_tags_by_room(room.id)
    tags= [tag.name for tag in tags]
    data.append({
        'cmd': 'add',
        'fields': {
            'id': room.id,
            'name': room.name,
            'intro': room.intro,
            'create_time': int(time.mktime(room.create_time.timetuple())),
            'tags': tags,
        }
    })
# for room_tag in room_tags:
#     data.append({
#         'cmd': 'add',
#         'fields': {
#             'id': room_tag.id,
#             'room_id': room_tag.room_id,
#             'tag_id': room_tag.tag_id,
#         }
#     })


post_data = {
    'action': 'push',
    'table_name': 'room',
    'items': json.dumps(data),
    'index_name': 'starmachine_room',
    'AccessKeyId': access_key_id,
    'SignatureMethod': 'HMAC-SHA1',
    'Version': 'v2',
    'SignatureVersion': '1.0',
    'SignatureNonce': str(time.time()),
    'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
}

format_para = format_parametr(post_data)
string_to_sign = 'POST&%s&%s' % (urllib.quote_plus('/'), urllib.quote_plus(format_para))
sign = encrypt_sign(string_to_sign)
post_data['Signature'] = sign
resp = requests.post(post_url, post_data)
import pdb; pdb.set_trace()