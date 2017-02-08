# coding: utf-8

import json
import logging
from tornado.web import MissingArgumentError
from starmachine.lib.utils import check_access_token
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, ROOM_NOT_FOUND, ACCESS_NOT_ALLOWED, SYSTEM_ERROR, \
    VOTE_NOT_FOUND, VOTE_OPTION_NOT_FOUND, OPTION_NOT_IN_VOTE, USER_HAS_ALREADY_VOTED, SENSITIVE_WORD_EXISTS, \
    OPTION_TEXT_TOO_LONG, USER_IN_ROOM_SILENT_LIST
from starmachine.model.user import User
from starmachine.model.room import Room
from starmachine.model.content.vote import Vote, VoteOption, VoteResult
from starmachine.sensitive_word.filter import filter
from starmachine.jobs.integral import handle_daily_create_content, handle_daily_vote_integral
from starmachine.model.room_user import RoomUser
from starmachine.model.consts import ROOM_USER_SILENT

logger = logging.getLogger(__name__)

class VoteHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            vote_id = self.get_argument('vote_id')
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

        vote = Vote.get(vote_id)
        if not vote:
            return self.error(VOTE_NOT_FOUND)

        return self.render({
            'status': 0,
            "data": {
                'vote': vote.jsonify(user),
            },
        })

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            name = self.get_argument('name')
            deadline = self.get_argument('deadline')
            options = self.get_argument('options')
            options = json.loads(options)
        except (MissingArgumentError, TypeError):
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(name):
            return self.error(SENSITIVE_WORD_EXISTS)

        for op in options:
            if filter.check_sensitive(op):
                return self.error(SENSITIVE_WORD_EXISTS)

            if len(op) > 24:
                return self.error(OPTION_TEXT_TOO_LONG)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        room_user = RoomUser.get_by_room_and_user(room_id, user_id)
        if not user.super_user:
            if not room_user:
                return self.error(ACCESS_NOT_ALLOWED)

        if int(room_user.status) == ROOM_USER_SILENT:
            return self.error(USER_IN_ROOM_SILENT_LIST)

        try:
            vote = Vote.add(user_id, room_id, name, deadline, options, room_user.status)
        except Exception as e:
            logger.error(u'添加投票失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        handle_daily_create_content.delay(user_id, vote.id)
        return self.render({
            'status': 0,
            'data': vote.jsonify(),
        })


class VoteOptionHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            vote_id = self.get_argument('vote_id')
            option_id = self.get_argument('vote_option_id')
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

        vote = Vote.get(vote_id)
        if not vote:
            return self.error(VOTE_NOT_FOUND)

        option = VoteOption.get(option_id)
        if not option:
            return self.error(VOTE_OPTION_NOT_FOUND)

        try:
            VoteResult.add(user_id, vote_id, option_id)
            return self.render({
                'status'
            })
        except:
            return self.error(SYSTEM_ERROR)


class VoteJoinedHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            vote_id = self.get_argument('vote_id')
            option_id = self.get_argument('option_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        vote = Vote.get(vote_id)
        if not vote:
            return self.error(VOTE_NOT_FOUND)

        option = VoteOption.get(option_id)
        if not option:
            return self.error(VOTE_OPTION_NOT_FOUND)

        if int(option.vote_id) != int(vote_id):
            return self.error(OPTION_NOT_IN_VOTE)

        if VoteResult.has_voted(vote_id, user_id):
            return self.error(USER_HAS_ALREADY_VOTED)

        VoteResult.add(user_id, vote_id, option_id)
        handle_daily_vote_integral.delay(user_id, vote_id)
        return self.render({
            'status': 0
        })



