# coding: utf-8

from starmachine.lib.utils import check_access_token
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import USER_NOT_FOUND
from starmachine.model.user import User
from starmachine.model.notify import Notify
from starmachine.model.content.content_like import ContentLiked
from starmachine.model.content.vote import VoteResult
from starmachine.model.content import Content
from starmachine.model.consts import VOTE_TYPE, NOTIFY_TYPE_SYSTEM, NOTIFY_TYPE_LIKED, NOTIFY_TYPE_COMMENT, NOTIFY_TYPE_REWARD

class UserNotifyHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        notify_type = self.get_argument('notify_type', NOTIFY_TYPE_SYSTEM)
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        notifies = Notify.get_notifies_by_type(user_id, notify_type, start, count)
        return self.render({
            'status': 0,
            'data': [notify.jsonify() for notify in notifies if notify],
        })


class UserNotifyCountHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        system_latest_notify = Notify.get_user_latest_notify_by_type(user_id, NOTIFY_TYPE_SYSTEM)
        liked_latest_notify = Notify.get_user_latest_notify_by_type(user_id, NOTIFY_TYPE_LIKED)
        comment_latest_notify = Notify.get_user_latest_notify_by_type(user_id, NOTIFY_TYPE_COMMENT)
        reward_latest_notify = Notify.get_user_latest_notify_by_type(user_id, NOTIFY_TYPE_REWARD)

        return self.render({
            'status': 0,
            'data': {
                'user_id': user_id,
                'notify': {
                    NOTIFY_TYPE_SYSTEM: {
                        'count': Notify.get_user_unread_notify_count_by_type(user_id, NOTIFY_TYPE_SYSTEM),
                        'latest_notify': system_latest_notify.jsonify() if system_latest_notify else None,
                    },
                    NOTIFY_TYPE_LIKED: {
                        'count': Notify.get_user_unread_notify_count_by_type(user_id, NOTIFY_TYPE_LIKED),
                        'latest_notify': liked_latest_notify.jsonify() if liked_latest_notify else None,
                    },
                    NOTIFY_TYPE_COMMENT: {
                        'count': Notify.get_user_unread_notify_count_by_type(user_id, NOTIFY_TYPE_COMMENT),
                        'latest_notify': comment_latest_notify.jsonify() if comment_latest_notify else None,
                    },
                    NOTIFY_TYPE_REWARD: {
                        'count': Notify.get_user_unread_notify_count_by_type(user_id, NOTIFY_TYPE_REWARD),
                        'latest_notify': reward_latest_notify.jsonify() if reward_latest_notify else None,
                    }
                },
            }
        })

