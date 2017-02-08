# coding: utf-8

import json
import logging
from datetime import datetime
from tornado.web import MissingArgumentError
from starmachine.lib.utils import check_access_token
from starmachine.lib.aliyun_oss import beijing_ali_oss
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import SYSTEM_ERROR, USER_NOT_FOUND, MISSING_PARAMS, CONTENT_NOT_FOUND, \
    ACCESS_NOT_ALLOWED, CONTENT_NOT_FOUND, ROOM_NOT_FOUND, SENSITIVE_WORD_EXISTS, USER_IN_ROOM_SILENT_LIST
from starmachine.model.user import User
from starmachine.model.content import Content
from starmachine.model.content.posts import Posts
from starmachine.model.content.vote import Vote
from starmachine.model.room import Room
from starmachine.model.content.content_like import ContentLiked
from starmachine.tools.postman import notify_content_like
from starmachine.sensitive_word.filter import filter
from starmachine.model.order.reward_order import RewardOrder
from starmachine.model.consts import ROOM_USER_SILENT
from starmachine.jobs.integral import handle_daily_create_content, handle_daily_send_like_integral
from starmachine.model.room_user import RoomUser

logger = logging.getLogger(__name__)

class PostsHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            posts_id = self.get_argument('posts_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        posts = Posts.get(posts_id)
        if not posts:
            return self.error(CONTENT_NOT_FOUND)

        return self.render({
            "status": 0,
            "data": posts.jsonify()
        })


    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        text = self.get_argument('text', '')
        room_id = self.get_argument('room_id')
        video = self.get_argument('video', '')
        images = self.get_argument('images', '[]')

        if not room_id:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(text):
            return self.error(SENSITIVE_WORD_EXISTS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room_user = RoomUser.get_by_room_and_user(room_id, user_id)
        if not user.super_user:
            if not room_user:
                return self.error(ACCESS_NOT_ALLOWED)

        if int(room_user.status) == ROOM_USER_SILENT:
            return self.error(USER_IN_ROOM_SILENT_LIST)

        try:
            posts = Posts.add(user_id, room_id, text, images, video, room_user.status)
        except Exception as e:
            logger.error(u'添加帖子内容失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        handle_daily_create_content.delay(user_id, posts.id)
        return self.render({
            'status': 0,
            'data': posts.jsonify()
        })


class ContentLikedHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            content_id = self.get_argument('content_id')
            room_id = self.get_argument('room_id')
        except AttributeError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(MISSING_PARAMS)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        if not user.has_room_access(room_id) or int(content.room_id) != int(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            liked_count = ContentLiked.add(content.id, content.content_type, user_id, content.creator_id)
            has_liked = ContentLiked.has_liked(content.id, user_id)
            if has_liked and (int(user_id) != int(content.creator_id)):
                notify_content_like.delay(user, content)
        except Exception as e:
            logger.error(u'添加点赞失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        if has_liked:
            handle_daily_send_like_integral.delay(user_id, content.creator_id)

        return self.render({
            'status': 0,
            'data': {
                'has_liked': bool(has_liked),
                'liked_count': liked_count,
            }
        })

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            content_id = self.get_argument('content_id')
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 20))
        except AttributeError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        if not user.has_room_access(room_id) or int(content.room_id) != int(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        liked_users = ContentLiked.get_liked_people(content_id, start, count)
        return self.render({
            'status': 0,
            'data': {
                'start': start,
                'count': count,
                'liked_users': [user.jsonify() for user in liked_users],
            }
        })


class ContentHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            content_id = self.get_argument('content_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        return self.render({
            "status": 0,
            "data": content.jsonify(user),
        })

    @check_access_token
    def delete(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            content_id = self.get_argument('content_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        try:
            content.delete()
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'删除内容失败。Content:[%s], Error:[%s]' % (content_id, e))
            return self.error(SYSTEM_ERROR)


class ContentRewardHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            content_id = self.get_argument('content_id')
            room_id = self.get_argument('room_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if not user.has_room_access(room_id) or int(content.room_id) != int(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        reward_orders = RewardOrder.get_reward_orders_by_content(content_id, start, count)
        data = []
        for reward_order in reward_orders:
            creator = User.get(reward_order.creator_id)
            amount = float(reward_order.amount)
            pay_time = reward_order.pay_time.strftime('%Y-%m-%d %H:%M:%S')
            data.append({
                'user': {
                    'id': creator.id,
                    'name': creator.user_name,
                    'avatar': creator.avatar_url,
                },
                'amount': amount,
                'pay_time': pay_time
            })

        return self.render({
            'status': 0,
            'data': data
        })


class ContentStatusHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            content_id = self.get_argument('content_id')
            room_id = self.get_argument('room_id')
            status = self.get_argument('status')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        content.update(status=status)
        return self.render({
            'status': 0,
        })