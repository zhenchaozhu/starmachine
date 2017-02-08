# coding: utf-8

import logging
from datetime import datetime
from tornado.web import MissingArgumentError
from starmachine.lib.utils import check_access_token
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, SYSTEM_ERROR, ALREADY_HAS_FOLLOWED, USER_NOT_FOLLOWED
from starmachine.model.user import User
from starmachine.model.friendship import UserFollows, UserFans
from starmachine.model.consts import FOLLOW_SINGLE_TYPE, FOLLOW_BOTH_TYPE
from starmachine.jobs.user import notify_be_followed

logger = logging.getLogger(__name__)

class FriendShipHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = self.get_argument('start', 0)
        count = self.get_argument('count', 10)

        rst = UserFollows.get_follows_by_user(user_id, start, count)
        data = []
        for d in rst:
            user = User.get(d.get('user_id'))
            follow_time = datetime.fromtimestamp(d.get('follow_time')).strftime('%Y-%m-%d %H:%M:%S')
            data.append({
                'id': user.id,
                'name': user.user_name,
                'avatar': user.avatar_url,
                'follow_time': follow_time
            })

        return self.render({
            'status': 0,
            'data': data
        })


    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            follow_id = self.get_argument('follow_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        follow = User.get(follow_id)
        if not follow:
            return self.error(USER_NOT_FOUND)

        if UserFollows.has_followed(user_id, follow_id):
            return self.error(ALREADY_HAS_FOLLOWED)

        if UserFollows.has_followed(follow_id, user_id):
            follow_type = FOLLOW_BOTH_TYPE
        else:
            follow_type = FOLLOW_SINGLE_TYPE

        try:
            UserFollows.follow(user_id, follow_id, follow_type)
            notify_be_followed.delay(user_id, follow_id)
            return self.error({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'添加关注失败。User:[%s] Follow:[%s] Error:[%s]' % (user_id, follow_id, e))
            return self.error(SYSTEM_ERROR)

    @check_access_token
    def delete(self):
        try:
            user_id = self.get_argument('user_id')
            follow_id = self.get_argument('follow_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        follow = User.get(follow_id)
        if not follow:
            return self.error(USER_NOT_FOUND)

        if not UserFollows.has_followed(user_id, follow_id):
            return self.error(USER_NOT_FOLLOWED)

        try:
            UserFollows.unfollow(user_id, follow_id)
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'取消关注失败。User:[%s], Follow:[%s], Error:[%s]' % (user_id, follow_id, e))
            return self.error(SYSTEM_ERROR)


class UserFansHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = self.get_argument('start', 0)
        count = self.get_argument('count', 10)
        rst = UserFans.get_fans_by_user(user_id, start, count)
        data = []
        for d in rst:
            user = User.get(d.get('user_id'))
            followed_time = datetime.fromtimestamp(d.get('followed_time')).strftime('%Y-%m-%d %H:%M:%S')
            data.append({
                'id': user.id,
                'name': user.user_name,
                'avatar': user.avatar_url,
                'follow_time': followed_time,
            })

        return self.render({
            'status': 0,
            'data': data,
        })


