# coding: utf-8

import logging
from tornado.web import MissingArgumentError
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, ACCESS_NOT_ALLOWED, ROOM_NOT_FOUND, \
    CONTENT_NOT_FOUND, SYSTEM_ERROR, REPLY_COMMENT_NOT_FOUND, SENSITIVE_WORD_EXISTS, USER_IN_ROOM_SILENT_LIST
from starmachine.model.comment import Comment
from starmachine.model.user import User
from starmachine.model.room import Room
from starmachine.model.content import Content
from starmachine.lib.utils import check_access_token
from starmachine.sensitive_word.filter import filter
from starmachine.tools.postman import notify_content_comment, notify_comment_reply
from starmachine.jobs.integral import handle_daily_comment

logger = logging.getLogger(__name__)

class ContentCommentHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            reply_user_id = self.get_argument('reply_user_id', None)
            room_id = self.get_argument('room_id')
            content_id = self.get_argument('content_id')
            text = self.get_argument('text')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(text):
            return self.error(SENSITIVE_WORD_EXISTS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        # if reply_user_id:
        #     reply_user = User.get(reply_user_id)
        #     if not reply_user:
        #         return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if not user.has_room_access(room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        if not user.has_room_speak_access(room_id):
            return self.error(USER_IN_ROOM_SILENT_LIST)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        try:
            comment = Comment.add(user_id, reply_user_id, content_id, text)
            if not reply_user_id:
                if int(user_id) != int(content.creator_id):
                    notify_content_comment.delay(user, content, comment)
                    handle_daily_comment.delay(user_id, comment.id)
            else:
                reply_user = User.get(reply_user_id)
                if not reply_user:
                    return self.error(USER_NOT_FOUND)

                if int(user.id) != int(reply_user_id):
                    notify_comment_reply.delay(user, reply_user, content, comment)
                    handle_daily_comment.delay(user_id, comment.id)

            return self.render({
                'status': 0,
                'data': comment.jsonify(),
            })
        except Exception as e:
            logger.error(u'发表评论失败。User:[%s], Content:[%s], Error:[%s]' % (user_id, content_id, e))
            return self.error(SYSTEM_ERROR)

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            content_id = self.get_argument('content_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except AttributeError:
            return self.error(MISSING_PARAMS)

        content = Content.get(content_id)
        if not content:
            return self.error(CONTENT_NOT_FOUND)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if not user.has_room_access(content.room_id):
            return self.error(ACCESS_NOT_ALLOWED)

        comments = Comment.get_comments_by_content(content_id, start, count)
        return self.render({
            'status': 0,
            'data': [comment.jsonify() for comment in comments],
        })

    @check_access_token
    def delete(self):
        try:
            user_id = self.get_argument('user_id')
            comment_id = self.get_argument('comment_id')
        except MissingArgumentError:
            return self.render(MISSING_PARAMS)

        comment = Comment.get(comment_id)
        if int(comment.user_id) != int(user_id):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            comment.delete()
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'删除评论内容失败。Comment:[%s], Error:[%s]' % (comment_id, e))
            return self.error(SYSTEM_ERROR)


