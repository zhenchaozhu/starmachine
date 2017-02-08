# coding: utf-8

import json
import logging
from tornado.web import MissingArgumentError
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token, init_pic_url
from starmachine.handlers.error import MISSING_PARAMS, SYSTEM_ERROR, USER_BACKGROUND_NOT_FOUND, USER_ROOM_BACKGROUND_NOT_FOUND
from starmachine.model.background import UserBackground, UserRoomBackground

logger = logging.getLogger(__name__)

class UserBackgroundHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        target_user_id = self.get_argument('target_user_id')
        user_background = UserBackground.get_by_user(target_user_id)
        if not user_background:
            return self.render({
                'status': 0,
                'data': '',
            })
        # if not user_background:
        #     return self.error(USER_BACKGROUND_NOT_FOUND)

        return self.render({
            'status': 0,
            'data': init_pic_url(user_background.short_url),
        })

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            image_url = self.get_argument('image_url')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        try:
            image_url = json.loads(image_url)[0]
        except:
            image_url = image_url

        user_background = UserBackground.get_by_user(user_id)
        if not user_background:
            try:
                UserBackground.add(user_id, image_url)
            except Exception as e:
                logger.error(u'设置背景图失败。User:[%s], Error:[%s]' % (user_id, e))
                return self.error(SYSTEM_ERROR)
        else:
            try:
                UserBackground.update(user_id, image_url)
            except Exception as e:
                logger.error(u'更新房间背景图失败。Error:[%s]' % e)
                return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })

    @check_access_token
    def put(self):
        try:
            user_id = self.get_argument('user_id')
            image_url = self.get_argument('image_url')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        try:
            UserBackground.update(user_id, image_url)
        except Exception as e:
            logger.error(u'更新房间背景图失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class UserRoomBackgroundHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        room_id = self.get_argument('room_id')
        user_room_background = UserRoomBackground.get_by_user_room(user_id, room_id)
        if not user_room_background:
            return self.render({
                'status': 0,
                'data': '',
            })
        # if not user_room_background:
        #     return self.error(USER_ROOM_BACKGROUND_NOT_FOUND)

        return self.render({
            'status': 0,
            'data': init_pic_url(user_room_background.short_url),
        })

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            image_url = self.get_argument('image_url')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user_room_background = UserRoomBackground.get_by_user_room(room_id, user_id)
        if not user_room_background:
            try:
                UserRoomBackground.add(user_id, room_id, image_url)
            except Exception as e:
                logger.error(u'设置背景图失败。User:[%s], Error:[%s]' % (user_id, e))
                return self.error(SYSTEM_ERROR)
        else:
            try:
                UserRoomBackground.update(user_id, room_id, image_url)
            except Exception as e:
                logger.error(u'更新用户房间背景图失败。Error:[%s]' % e)
                return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })

    @check_access_token
    def put(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            image_url = self.get_argument('image_url')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        try:
            UserRoomBackground.update(user_id, room_id, image_url)
        except Exception as e:
            logger.error(u'更新用户房间背景图失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })
