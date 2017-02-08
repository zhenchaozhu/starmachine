# coding: utf-8

from __future__ import division
import re
import json
import time
import logging
import calendar
import urllib
from urlparse import urlparse
from datetime import datetime, timedelta
# from apscheduler.schedulers.tornado import TornadoScheduler
from tornado.web import MissingArgumentError, HTTPError, asynchronous, gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from starmachine.handlers.base import BaseHandler, APIBaseHandler
from starmachine.model.room import Room
from starmachine.lib.utils import check_access_token, init_pic_url
from starmachine.lib.tornado_scheduler import tornado_scheduler
from starmachine.handlers.error import MISSING_PARAMS, ROOM_NAME_COULD_NOT_NONE, ROOM_CREATE_ERROR, ROOM_NAME_EXISTS, \
    ROOM_NOT_FOUND, USER_NOT_FOUND, ACCESS_NOT_ALLOWED, CONTENT_NOT_FOUND, SYSTEM_ERROR, \
    SENSITIVE_WORD_EXISTS, ROOM_PUSH_OVER_LIMIT, ROOM_STAR_FUND_NOT_ENOUGH, ROOM_ADMIN_USER_OVER_LIMIT
from starmachine.model.consts import LIMIT_USER_NUMBER, ROOM_PUBLIC, CONTENT_PUBLIC, ROOM_USER_NORMAL, REPORT_ROOM_CONTENT, \
    ROOM_ADMIN_USER_MAX_AMOUNT
from starmachine.model.user import User
from starmachine.model.room_user import RoomUser
from starmachine.model.content import Content
from starmachine.jobs.user import push_room_content
from starmachine.jobs.opensearch import add_open_search_room, update_open_search_room
from starmachine.model.room_tag import RoomTag
from starmachine.sensitive_word.filter import filter, filter_name
from starmachine.model.room_push import RoomPush
from starmachine.model.report import Report
from starmachine.model.star_fund_record import StarFundRecord
from starmachine.lib.ali_open_search import index, access_key_id, format_parametr, encrypt_sign, search_host
from starmachine.jobs.room import room_remove_user_notify, room_silent_user_notify

logger = logging.getLogger(__name__)
IMAGE_TYPE_LIST = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']

def remove_room_silent_user(room_id, user_id, status):
    RoomUser.remove_user_silent(room_id, user_id, status)

class RoomPageShareHandler(BaseHandler):

    def get(self, room_id):
        room = Room.get(room_id)
        if not room:
            raise HTTPError(404)

        context = {
            'room': room,
        }
        self.render('share.html', **context)

class RoomHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        data = {
            'status': 0,
            'data': room.jsonify(user),
        }

        return self.render(data)

    @check_access_token
    def post(self, *args):
        try:
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
            tag_ids = self.get_argument('tag_ids', '[]')
            intro = self.get_argument('intro', '')
            limit_user_number = self.get_argument('limit_user_number', LIMIT_USER_NUMBER)
            status = self.get_argument('status', ROOM_PUBLIC)
            avatar_url = self.get_argument('avatar', '')
            question_info = self.get_argument('question_info', None)
            create_time = datetime.now()
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(name) or filter.check_sensitive(intro) or filter_name.check_sensitive(name):
            return self.error(SENSITIVE_WORD_EXISTS)

        try:
            tag_ids = json.loads(tag_ids)
        except ValueError:
            tag_ids = []

        if not name:
            return self.error(ROOM_NAME_COULD_NOT_NONE)

        if Room.exist_room(name):
            return self.error(ROOM_NAME_EXISTS)

        try:
            avatar = json.loads(avatar_url)[0]
        except:
            avatar = avatar_url

        if question_info:
            question_info = json.loads(question_info)

        try:
            room_id = Room.add(user_id, name, intro, tag_ids, avatar, limit_user_number, create_time, status, question_info)
            add_open_search_room.delay(room_id, name, intro, create_time, tag_ids)
        except Exception, e:
            logger.error(u'创建房间失败。error:[%s]', e)
            return self.error(ROOM_CREATE_ERROR)

        room = Room.get(room_id)
        data = {
            'status': 0,
            'data': room.jsonify(),
        }

        return self.render(data)

    @check_access_token
    def put(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            name = self.get_argument('name')
            tag_ids = self.get_argument('tag_ids', [])
            intro = self.get_argument('intro', '')
            limit_user_number = self.get_argument('limit_user_number', LIMIT_USER_NUMBER)
            status = self.get_argument('status', ROOM_PUBLIC)
            avatar_url = self.get_argument('avatar', '')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(name) or filter.check_sensitive(intro) or filter_name.check_sensitive(name):
            return self.error(SENSITIVE_WORD_EXISTS)

        try:
            tag_ids = json.loads(tag_ids)
        except ValueError:
            tag_ids = []

        try:
            avatar = json.loads(avatar_url)[0]
        except:
            avatar = avatar_url

        o = urlparse(avatar)
        img_path = o.path
        if img_path.startswith('/'):
            avatar = re.sub(r'/', '', img_path, 1)
        else:
            avatar = img_path

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if RoomTag.get_tag_ids_by_room(room_id) != tag_ids:
            RoomTag.update_tags(room_id, tag_ids)

        try:
            room.update(name=name, intro=intro, limit_user_number=limit_user_number, status=status, avatar=avatar)
            update_open_search_room.delay(room_id, name, intro, tag_ids)
        except Exception, e:
            logger.error(u'更新房间失败。error:[%s]', e)
            return self.error(SYSTEM_ERROR)

        room = Room.get(room_id)
        data = {
            'status': 0,
            'data': room.jsonify(),
        }

        return self.render(data)


class RoomContentHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        contents = Content.gets_by_room(room_id, user_id, start, count)
        data = []
        for content in contents:
            try:
                rst = content.jsonify(user)
                rst.update({
                    'room_user_status': content.room_user_status,
                })
                data.append(rst)
            except Exception as e:
                logger.warning(u'获取内容数据失败。Content:[%s], Error:[%s]' % (content.id, e))
                continue

        return self.render({
            'status': 0,
            'data': data,
        })


class RoomPushHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = int(self.get_argument('user_id'))
            room_id = int(self.get_argument('room_id'))
            content_id = self.get_argument('content_id')
            text = self.get_argument('text')
            start_time = self.get_argument('start_time', None)
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        now = datetime.now()
        if filter.check_sensitive(text):
            return self.error(SENSITIVE_WORD_EXISTS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        if int(room.creator_id) != user_id or int(content.room_id) != room_id:
            return self.error(ACCESS_NOT_ALLOWED)

        push_count = RoomPush.get_push_count_by_room_and_date(room_id, now)
        if push_count and push_count >= 1:
            return self.error(ROOM_PUSH_OVER_LIMIT)

        push_room_content.delay(room, content, text, start_time)
        return self.render({
            'status': 0,
        })


class RoomSearch(APIBaseHandler):

    @check_access_token
    @gen.coroutine
    def get(self):
        start = self.get_argument('start', 0)
        count = self.get_argument('count', 10)
        query = self.get_argument('query', '').encode('utf-8')
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        if query:
            http_client = AsyncHTTPClient()
            params = {
                'fetch_fields': 'id',
                'query': "query=name:'%s' OR tags:'%s'&&sort=-create_time&&config=start:%s,hit:%s" % (query, query, start, count),
                'index_name': index,
                'AccessKeyId': access_key_id,
                'SignatureMethod': 'HMAC-SHA1',
                'Version': 'v2',
                'SignatureVersion': '1.0',
                'SignatureNonce': str(time.time()),
                'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            }
            format_params = format_parametr(params)
            string_to_sign = 'GET&%s&%s' % (urllib.quote_plus('/'), urllib.quote_plus(format_params))
            sign = encrypt_sign(string_to_sign)
            params['Signature'] = sign
            search_url = url_concat(search_host, params)
            resp = yield http_client.fetch(search_url)
            if resp.code == 200:
                data = json.loads(resp.body)
                if data.get('status') == 'OK':
                    result = data.get('result')
                    total = result.get('total')
                    items = result.get('items')
                    if items:
                        room_ids = [item.get('id') for item in items]
                        rst = []
                        for room_id in room_ids:
                            room = Room.get(room_id)
                            if room:
                                rst.append(room.jsonify(user))

                        self.render({
                            'status': 0,
                            'data': {
                                'way': 'search',
                                'total': total,
                                'items': rst,
                            },
                        })
                        return
            else:
                self.error(SYSTEM_ERROR)
                return

        self.render({
            'status': 0,
            'data': {
                'items': [],
            }
        })
        return


class RoomUserHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            users = room.get_users(start, count)
            return self.render({
                'status': 0,
                'data': [user.jsonify() for user in users]
            })
        except Exception as e:
            logger.error(u'获取房间用户失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class RoomOrderUserHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        # if not user.has_room_access(room_id):
        #     return self.error(ACCESS_NOT_ALLOWED)

        room_users = RoomUser.get_ordered_room_users_by_room(room_id, start, count)
        data = []
        for room_user in room_users:
            user_id = room_user.user_id
            user = User.get(user_id)
            status = room_user.status
            data.append({
                'id': user.id,
                'name': user.user_name,
                'avatar': user.avatar_url,
                'status': status,
                'join_time': room_user.join_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return self.render({
            'status': 0,
            'data': data,
        })


class RoomUserRewardRankHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        # if not user.has_room_access(room_id):
        #     return self.error(ACCESS_NOT_ALLOWED)

        room = Room.get(room_id)
        rst = room.get_reward_rank(start, count)
        data = []
        for info in rst:
            user_id = info.get('user_id')
            user = User.get(user_id)
            data.append({
                'user': {
                    'id': user.id,
                    'name': user.user_name,
                    'avatar': user.avatar_url,
                },
                'reward_amount': info.get('amount') / 100,
            })

        return self.render({
            'status': 0,
            'data': data,
        })


class RoomAdminHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = int(self.get_argument('user_id'))
            room_id = self.get_argument('room_id')
            admin_id = int(self.get_argument('admin_id'))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) != user_id or user_id == admin_id:
            return self.error(ACCESS_NOT_ALLOWED)

        if not RoomUser.room_exists_user(room_id, admin_id):
            return self.error(ACCESS_NOT_ALLOWED)

        room_admin_count = RoomUser.get_room_admin_count(room_id)
        if room_admin_count >= ROOM_ADMIN_USER_MAX_AMOUNT:
            return self.error(ROOM_ADMIN_USER_OVER_LIMIT)

        try:
            RoomUser.set_room_admin(room_id, admin_id)
        except Exception as e:
            logger.error(u'添加房间管理员失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })

    @check_access_token
    def delete(self):
        try:
            user_id = int(self.get_argument('user_id'))
            room_id = self.get_argument('room_id')
            admin_id = self.get_argument('admin_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) != user_id:
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            RoomUser.delete_room_admin(room_id, admin_id)
        except Exception as e:
            logger.error(u'删除管理员失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class RoomUserSilentHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            room_id = self.get_argument('room_id')
            user_id = self.get_argument('user_id')
            silent_user_id = self.get_argument('silent_user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        set_time = datetime.now()
        operator = User.get(user_id)
        silent_user = User.get(silent_user_id)
        if not silent_user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        room_operator = RoomUser.get_by_room_and_user(room_id, user_id)
        room_silent_user = RoomUser.get_by_room_and_user(room_id, silent_user_id)
        operator_status = room_operator.status
        if not room_operator.has_room_user_handle_access(room_silent_user):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            RoomUser.set_user_silent(room_id, silent_user_id, set_time)
        except Exception as e:
            logger.error(u'用户房间禁言失败。User:[%s], Room:[%s], Error:[%s]' % (silent_user_id, room_id, e))
            return self.error(SYSTEM_ERROR)

        self.render({
            'status': 0,
        })
        room_silent_user_notify.delay(operator, operator_status, room, silent_user)
        # scheduler = TornadoScheduler()
        # scheduler.add_jobstore('redis', jobs_key='room_user:silent:jobs', run_times_key='room_user:remove_silent')
        run_date = set_time + timedelta(days=1)
        tornado_scheduler.add_job(remove_room_silent_user, 'date', run_date=run_date, args=[room_id, user_id, room_silent_user.status])
        # scheduler.start()
        return


class RoomUserRemoveHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            room_id = self.get_argument('room_id')
            user_id = self.get_argument('user_id')
            remove_user_id = self.get_argument('remove_user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        operator = User.get(user_id)
        remove_user = User.get(remove_user_id)
        if not remove_user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        room_operator = RoomUser.get_by_room_and_user(room_id, user_id)
        room_remove_user = RoomUser.get_by_room_and_user(room_id, remove_user_id)
        if not room_operator.has_room_user_handle_access(room_remove_user):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            RoomUser.remove_and_black_user(room_id, remove_user_id)
        except Exception as e:
            logger.error(u'房间删除拉黑用户失败。User:[%s], Room:[%s], Error:[%s]' % (remove_user_id, room_id, e))
            return self.error(SYSTEM_ERROR)

        self.render({
            'status': 0,
        })
        room_remove_user_notify(operator, room_operator.status, room, remove_user)
        return


class RoomSerialUserHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            room_id = self.get_argument('user_id')
            start = int(self.get_argument('start'))
            end = int(self.get_argument('end'))
        except (MissingArgumentError, ValueError):
            return self.error(MISSING_PARAMS)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        try:
            users = room.get_users_by_serial_number(start, end)
            return self.render({
                'status': 0,
                'data': [user.jsonify() for user in users]
            })
        except Exception as e:
            logger.error(u'根据序列号获取房间成员失败。Room:[%s], Error:[%s]' % (room_id, e))
            return self.error(SYSTEM_ERROR)


class RoomAvatarHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id', '')
            avatar_url = self.get_argument('avatar_url')
            room_id = self.get_argument('room_id')
        except (MissingArgumentError, KeyError):
            return self.error(MISSING_PARAMS)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        try:
            avatar = json.loads(avatar_url)[0]
        except:
            avatar = avatar_url

        room.update(avatar=avatar)
        return self.render({
            'status': 0,
            'data': {
                'avatar': init_pic_url(avatar)
            }
        })


class RoomNameUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            name = self.get_argument('name')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(name):
            return self.error(SENSITIVE_WORD_EXISTS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) != int(user_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            if name != room.name:
                if room.exist_room(name):
                    return self.error(ROOM_NAME_EXISTS)
                else:
                    room.update(name=name)

            return self.render({
                'status': 0,
                'data': {
                    'name': name,
                }
            })
        except Exception as e:
            logger.error(u'修改房间名失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class RoomIntroUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            intro = self.get_argument('intro')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(intro):
            return self.error(SENSITIVE_WORD_EXISTS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) != int(user_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            if intro != room.intro:
                room.update(intro=intro)

            return self.render({
                'status': 0,
                'data': {
                    'intro': intro,
                }
            })
        except Exception as e:
            logger.error(u'修改房间介绍失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class RoomTagUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            tag_ids = self.get_argument('tag_ids')
            tag_ids = json.loads(tag_ids)
        except (MissingArgumentError, TypeError):
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) != int(user_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            RoomTag.update_tags(room_id, tag_ids)
            tags = RoomTag.get_tags_by_room(room_id)
            return self.render({
                'status': 0,
                'data': {
                    'tags': [tag.jsonify() for tag in tags]
                }
            })
        except Exception as e:
            logger.error(u'修改房间标签信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class RoomStatusUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            status = int(self.get_argument('status'))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) != int(user_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            if status != int(room.status):
                room.update(status=status)

            return self.render({
                'status': 0,
                'data': {
                    'status': status,
                }
            })
        except Exception as e:
            logger.error(u'修改房间状态失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class RoomFundHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        result = []
        now = datetime.now()
        for delta in xrange(1, 5):
            year, month, max_day = self.add_months(now, delta)
            # start_day = datetime(year=year, month=month, day=1).strftime('%Y-%m-%d')
            end_day = (datetime(year=year, month=month, day=max_day) + timedelta(days=1)).strftime('%Y-%m-%d')
            # amount = RoomOrder.get_fund_amount_by_room_and_month(room_id, end_day)
            amount = 0
            result.append({
                'month': month,
                'amount': amount
            })

        return self.render({
            'status': 0,
            'data': result
        })

    def add_months(self, date, delta):
        month = date.month - 1 + delta
        year = date.year + month / 12
        month = month % 12 + 1
        cal = calendar.monthrange(year, month)
        return year, month, cal[1]


class RoomIncreaseRankHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        now = datetime.now()
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        user_id = self.get_argument('user_id')
        year = self.get_argument('year', now.year)
        month = self.get_argument('month', now.month)
        user = User.get(user_id)
        rst = Room.get_rooms_increase_rank(year, month, start, count)
        data = []
        for d in rst:
            room_id = d.get('room_id')
            increase = d.get('increase')
            room = Room.get(room_id)
            data.append({
                # 'room': {
                #     'id': room.id,
                #     'name': room.name,
                #     'avatar_url': room.avatar_url,
                #     'user_amount': room.user_amount,
                # },
                'room': room.jsonify(user),
                'increase': increase,
            })

        return self.render({
            'status': 0,
            'data': {
                'year': year,
                'month': month,
                'data': data
            },
        })


class RoomContentReportHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            reporter_id = self.get_argument('user_id')
            content_id = self.get_argument('content_id')
            room_id = int(self.get_argument('room_id'))
            reason = self.get_argument('reason', '')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        content = Content.get(content_id)
        if int(content.room_id) != room_id:
            return self.error(ACCESS_NOT_ALLOWED)

        user = User.get(reporter_id)
        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            Report.add(reporter_id, REPORT_ROOM_CONTENT, content_id, reason)
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'添加举报失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class RoomStarFundRecordHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        star_fund_records = StarFundRecord.gets_by_room(room_id, start, count)
        data = []
        for star_fund_record in star_fund_records:
            data.append({
                'id': star_fund_record.id,
                'room_id': star_fund_record.room_id,
                'source': star_fund_record.source,
                'amount': float(star_fund_record.amount),
                'create_time': star_fund_record.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return self.render({
            'status': 0,
            'data': data,
        })