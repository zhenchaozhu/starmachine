# coding: utf-8

import json
import logging
import hashlib
import random
from datetime import datetime
from tornado.web import MissingArgumentError, HTTPError
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token, init_pic_url, get_str_length
from starmachine.lib.redis_cache import CacheManager
from starmachine.handlers.error import USER_NOT_FOUND, GET_RONG_TOKEN_FAIL, ACCESS_NOT_ALLOWED, SYSTEM_ERROR, \
    GROUP_NOT_FOUND, USER_IN_GROUP_BLACK_LIST, USER_ALREADY_IN_GROUP, MISSING_PARAMS, FLOWER_USER_NAME_EXISTS, \
    FLOWER_USER_NAME_UPDATE_OVER_LIMIT, FLOWER_USER_INFO_NOT_SET, USER_NOT_IN_GROUP, GROUP_CREATED_COUNT_OVER_LIMIT, \
    GROUP_IS_FULL, GROUP_ENVELOPE_NOT_FOUND, GROUP_ENVELOPE_HAS_OPENED, GROUP_NAME_EXISTS, USER_JOIN_GROUP_OVER_LIMIT, \
    GROUP_NAME_LESS_MINIMUM_LIMIT, GROUP_NAME_OVER_MAXIMUM_LIMIT, GROUP_ANNOUNCEMENT_OVER_MAXIMUM_LIMIT, \
    FLOWER_NAME_LESS_MINIMUM_LIMIT, FLOWER_NAME_OVER_MAXIMUM_LIMIT
from starmachine.model.user import User
from starmachine.model.rong import RongToken, UserChatStatus
from starmachine.model.friendship import UserFollows
from starmachine.rong.rong_client import rong_client
from starmachine.model.group import Group, GroupVoiceTime
from starmachine.model.group_user import GroupUser, GroupBlackUser
from starmachine.model.flower_user import FlowerUser, flower_user_name_update_limit_key, \
    flower_user_name_update_limit_time
from starmachine.model.consts import GROUP_USER_NORMAL, CHAT_NORMAL_IDENTITY, CHAT_FLOWER_IDENTITY, FLOWER_AVATAR_ARR, \
    REPORT_GROUP, GROUP_USER_LIMIT
from starmachine.model.group_message_liked import GroupMessageLiked, GroupMessage
from starmachine.jobs.group import chat_user_reward
from starmachine.model.report import Report
from starmachine.model.group_envelope import GroupEnvelope

logger = logging.getLogger(__name__)

class GetTokenHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        rong_token = RongToken.get_rong_token_by_user(user_id)
        if not rong_token:
            rst = rong_client.user_get_token(user_id, user.name, user.avatar_url)
            if rst.get('code') == 200:
                token = rst.get('token')
                RongToken.add(user_id, token)
            else:
                logger.error(u'获取融云token失败。Info:[%s]' % (json.dumps(rst)))
                return self.error(GET_RONG_TOKEN_FAIL)
        else:
            token = rong_token.token

        return self.render({
            'status': 0,
            'data': {
                'token': token,
                'flower_identity': UserChatStatus.is_flower_identity(user_id),
            }
        })


class GroupHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        group_id = self.get_argument('group_id')
        group = Group.get(group_id)
        user = User.get(user_id)
        if not group:
            return self.error(GROUP_NOT_FOUND)

        return self.render({
            'status': 0,
            'data': group.jsonify(user),
        })

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        name = self.get_argument('name')
        announcement = self.get_argument('announcement', '')
        avatar = self.get_argument('avatar', '')
        if Group.is_over_create_limit(user_id):
            return self.error(GROUP_CREATED_COUNT_OVER_LIMIT)

        if Group.exists_group(name):
            return self.error(GROUP_NAME_EXISTS)

        if get_str_length(name) < 4:
            return self.error(GROUP_NAME_LESS_MINIMUM_LIMIT)

        if get_str_length(name) > 60:
            return self.error(GROUP_NAME_OVER_MAXIMUM_LIMIT)

        if announcement:
            if get_str_length(announcement) > 100:
                return self.error(GROUP_ANNOUNCEMENT_OVER_MAXIMUM_LIMIT)

        try:
            group = Group.add(user_id, avatar, name, announcement)
        except Exception as e:
            logger.error(u'创建群组失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': group.jsonify(user),
        })

    @check_access_token
    def delete(self):
        user_id = int(self.get_argument('user_id'))
        group_id = self.get_argument('group_id')
        group = Group.get(group_id)
        if group.creator_id != user_id:
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            group.delete()
            rong_client.group_dismiss(user_id, group_id)
        except Exception as e:
            logger.error(u'删除群组失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class GroupAvatarUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        group_id = self.get_argument('group_id')
        group = Group.get(group_id)
        avatar = self.get_argument('avatar')
        group.update(avatar=avatar)
        return self.render({
            'status': 0,
            'data': {
                'portraitUri': init_pic_url(avatar),
            }
        })


class GroupAnnouncementUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        group_id = self.get_argument('group_id')
        announcement = self.get_argument('announcement')
        if announcement:
            if get_str_length(announcement) > 100:
                return self.error(GROUP_ANNOUNCEMENT_OVER_MAXIMUM_LIMIT)

        group = Group.get(group_id)
        group.update(announcement=announcement)
        return self.render({
            'status': 0,
        })


class GroupNameUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        group_id = self.get_argument('group_id')
        name = self.get_argument('name')
        group = Group.get(group_id)
        if name != group.name:
            if group.exists_group(name):
                return self.error(GROUP_NAME_EXISTS)
            else:
                if get_str_length(name) < 4:
                    return self.error(GROUP_NAME_LESS_MINIMUM_LIMIT)

                if get_str_length(name) > 60:
                    return self.error(GROUP_NAME_OVER_MAXIMUM_LIMIT)
                group.update(name=name)

        return self.render({
            'status': 0,
        })


class GroupListHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        user_id = self.get_argument('user_id')
        groups = Group.get_groups_order_by_user_amount(start, count)
        user = User.get(user_id)

        return self.render({
            'status': 0,
            'data': [group.jsonify(user) for group in groups],
        })


class GroupUserHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        group_id = self.get_argument('group_id')
        group = Group.get(group_id)
        user = User.get(user_id)
        if not group:
            return self.error(GROUP_NOT_FOUND)

        if group.exists_user(user_id):
            return self.error(USER_ALREADY_IN_GROUP)

        if GroupUser.is_over_join_limit(user_id):
            return self.error(USER_JOIN_GROUP_OVER_LIMIT)

        if GroupBlackUser.is_group_black_user(group_id, user_id):
            return self.error(USER_IN_GROUP_BLACK_LIST)

        if group.user_amount >= group.limit_user:
            pressed_user_id = GroupUser.get_pressed_user_by_group(group_id)
            if not pressed_user_id:
                return self.error(GROUP_IS_FULL)
            else:
                group_user = GroupUser.get_by_group_and_user(group_id, user_id)
                group_user.delete()

        try:
            GroupUser.add_group_user(group.id, group.name, user_id, GROUP_USER_NORMAL)
        except Exception as e:
            logger.error(u'加入群组失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })

    @check_access_token
    def delete(self):
        user_id = int(self.get_argument('user_id'))
        group_id = self.get_argument('group_id')
        group = Group.get(group_id)
        if not group:
            return self.error(GROUP_NOT_FOUND)

        group_user = GroupUser.get_by_group_and_user(group_id, user_id)
        if not group_user:
            return self.error(USER_NOT_IN_GROUP)

        try:
            group_user.delete()
        except Exception as e:
            logger.error(u'退出群组失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0
        })


class GroupUserRemoveHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            group_id = self.get_argument('group_id')
            user_id = self.get_argument('user_id')
            remove_user_id = self.get_argument('remove_user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        operator = User.get(user_id)
        remove_user = User.get(remove_user_id)
        if not remove_user:
            return self.error(USER_NOT_FOUND)

        group = Group.get(group_id)
        if not group:
            return self.error(GROUP_NOT_FOUND)

        group_operator = GroupUser.get_by_group_and_user(group_id, user_id)
        remove_group_user = GroupUser.get_by_group_and_user(group_id, remove_user_id)
        if not group_operator.has_group_user_handle_access(remove_group_user):
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            GroupUser.remove_and_black_user(group_id, remove_user_id)
        except Exception as e:
            logger.error(u'群组删除拉黑用户失败。User:[%s], GROUP:[%s], Error:[%s]' % (remove_user_id, group_id, e))
            return self.error(SYSTEM_ERROR)

        self.render({
            'status': 0,
        })
        # 先不加上通知
        # room_remove_user_notify(operator, room_operator.status, room, remove_user)
        return


class GroupSyncHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        group_ids = GroupUser.get_user_joined_groups(user_id)
        data = {}
        for group_id in group_ids:
            group = Group.get(group_id)
            data.update({
                group_id: group.name
            })

        try:
            self.group_async(user_id, data, 0, 3)
        except:
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })

    def group_async(self, user_id, data, retry_no, retry_times):
        try:
            rong_client.group_sync(user_id, data)
        except Exception as e:
            if retry_no < retry_times:
                retry_no += 1
                logger.warning(u'同步用户群组信息失败。Error:[%s]' % e)
                self.group_async(user_id, data, retry_no, retry_times)
            else:
                logger.error(u'同步用户群组信息失败。Error:[%s]' % e)
                raise


class FlowerUserHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        group_user_info = FlowerUser.get_by_user(user_id)
        if not group_user_info:
            return self.error(FLOWER_USER_INFO_NOT_SET)

        return self.render({
            'status': 0,
            'data': group_user_info.jsonify() if group_user_info else {},
        })

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if FlowerUser.exists_name(name):
            return self.error(FLOWER_USER_NAME_EXISTS)

        if get_str_length(name) < 2:
            return self.error(FLOWER_NAME_LESS_MINIMUM_LIMIT)

        if get_str_length(name) > 20:
            return self.error(FLOWER_NAME_OVER_MAXIMUM_LIMIT)

        group_user_info = FlowerUser.get_by_user(user_id)
        if not group_user_info:
            try:
                random_name = random.choice(FLOWER_AVATAR_ARR)
                avatar_uri = 'static/avatar/flower/image_huaming_%s@2x.png' % random_name
                group_user_info = FlowerUser.add(user_id, name, avatar_uri)
            except Exception as e:
                logger.error(u'添加用户花名成功。Error:[%s]' % e)
                return self.error(SYSTEM_ERROR)
        else:
            try:
                cache = CacheManager().cache
                redis_key = flower_user_name_update_limit_key % user_id
                if cache.exists(redis_key):
                    update_count = cache.get(redis_key)
                    if int(update_count) >= 3:
                        return self.error(FLOWER_USER_NAME_UPDATE_OVER_LIMIT)
                    else:
                        group_user_info.update_name(name)
                        cache.incr(redis_key, 1)
                else:
                    group_user_info.update_name(name)
                    cache.set(redis_key, 1)
                    cache.expire(redis_key, flower_user_name_update_limit_time)
            except Exception as e:
                logger.error(u'更新用户花名失败。Error:[%s]', e)
                return self.error(SYSTEM_ERROR)

        if UserChatStatus.is_flower_identity(user_id):
            rong_client.user_refresh(user_id, name=name)

        return self.render({
            'status': 0,
            'data': {
                'left_change_times': group_user_info.left_change_times(),
            }
        })


class FlowerUserAvatarHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            avatar = self.get_argument('avatar')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        group_user_info = FlowerUser.get_by_user(user_id)
        if not group_user_info:
            return self.error(FLOWER_USER_INFO_NOT_SET)

        try:
            group_user_info.update(avatar=avatar)
        except Exception as e:
            logger.error(u'更新群组用户头像信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        if UserChatStatus.is_flower_identity(user_id):
            rong_client.user_refresh(user_id, portrait_uri=init_pic_url(avatar))

        return self.render({
            'status': 0,
            'data': {
                'portraitUri': init_pic_url(avatar),
            }
        })


class GroupSearchHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        query = self.get_argument('query', '')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        if query:
            rst = []
            groups = Group.search_group(query, start ,count)
            for group in groups:
                rst.append(group.jsonify(user))

            return self.render({
                'status': 0,
                'data': {
                    'items': rst,
                },
            })

        return self.render({
            'status': 0,
            'data': {
                'items': [],
            }
        })


class GroupMessageLikedHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        group_id = self.get_argument('group_id')
        message_liked_info = GroupMessageLiked.get_liked_message_amount_by_group(group_id)
        liked_messages = GroupMessageLiked.get_liked_message_by_user_and_group(user_id, group_id)
        return self.render({
            'status': 0,
            'data': {
                'liked_messages': liked_messages,
                'message_liked_info': message_liked_info,
            }
        })

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            group_id = self.get_argument('group_id')
            message_id = self.get_argument('message_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        message = GroupMessage.get(message_id)
        helper = User.get(user_id)
        receiver = User.get(message.creator_id)
        try:
            liked_count = GroupMessageLiked.add(user_id, group_id, message_id)
            GroupMessage.update_amount(message_id, liked_count)
            if liked_count and liked_count % 2 == 0:
                chat_user_reward.delay(receiver, helper, group_id, message_id, liked_count)

            has_liked = GroupMessageLiked.has_liked(user_id, group_id, message_id)
        except Exception as e:
            logger.error(u'添加点赞失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': {
                'has_liked': bool(has_liked),
                'liked_count': liked_count,
            }
        })


class GroupUserListHandle(APIBaseHandler):

    @check_access_token
    def get(self):
        group_id = self.get_argument('group_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))

        group_user_ids = GroupUser.get_users_by_group(group_id, start, count)
        group_users = []
        for group_user_id in group_user_ids:
            if UserChatStatus.is_flower_identity(group_user_id):
                group_user = FlowerUser.get_by_user(group_user_id)
            else:
                group_user = User.get(group_user_id)

            group_users.append({
                'userId': group_user_id,
                'name': group_user.user_name,
                'portraitUri': group_user.avatar_url,
            })

        return self.render({
            'status': 0,
            'data': group_users,
        })


class GroupVoiceTimeHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        group_id = self.get_argument('group_id')
        user_id = self.get_argument('user_id')
        GroupUser.update_voice_time(group_id, user_id)
        return self.render({
            'status': 0,
        })


class UserJoinedGroupsHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        # start = int(self.get_argument('start', 0))
        # count = int(self.get_argument('count', 10))
        user = User.get(user_id)
        joined_group_ids = GroupUser.get_user_joined_groups(user_id)
        data = [Group.get(group_id).jsonify(user) for group_id in joined_group_ids]
        return self.render({
            'status': 0,
            'data': data,
        })


class UserCreatedGroupsHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        user = User.get(user_id)
        created_groups = Group.get_groups_by_user(user_id, start, count)
        return self.render({
            'status': 0,
            'data': [group.jsonify(user) for group in created_groups],
        })

class GroupMessageNotify(APIBaseHandler):

    def post(self):
        # timestamp = self.get_arguments('timestamp')[0]
        # signature = self.get_argument('signature')
        # nonce = self.get_argument('nonce')
        # object_name = self.get_argument('objectName')
        # msg_timestamp = self.get_argument('msgTimestamp')
        # creator_id = self.get_argument('fromUserId')
        # group_id = self.get_argument('toUserId')
        # channel_type = self.get_argument('channelType')
        # content = self.get_argument('content')
        # content_obj = json.loads(content)
        # msg_timestamp = int(msg_timestamp) / 1000
        # local_signature = hashlib.sha1(app_secret + nonce + timestamp).hexdigest()
        # if signature == local_signature:
        #     message_id = content_obj.get('extra')
        #     # message_id = '%s%s%s' % (creator_id, group_id, msg_timestamp) # id生成精确到秒级别
        #     create_time = datetime.fromtimestamp(msg_timestamp) # 精确到秒级别
        #     try:
        #         GroupMessage.add(message_id, creator_id, group_id, object_name, channel_type, content, create_time)
        #         return self.render({
        #             'status': 0,
        #         })
        #     except Exception as e:
        #         logger.error(u'添加消息失败。Error:[%s] post_arguments:[%s]' % (e, self.request.arguments))
        #         return self.error(SYSTEM_ERROR)
        # else:
        #     raise HTTPError(403)
        return self.render({
            'status': 0,
        })


class GroupHotMessageHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        count = int(self.get_argument('count', 10))
        group_id = self.get_argument('group_id')
        user = User.get(user_id)
        messages = GroupMessage.get_hot_messages(group_id, count)
        return self.render({
            'status': 0,
            'data': [message.jsonify(user) for message in messages],
        })


class GroupSwitchIdentityHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        chat_status = int(self.get_argument('chat_status'))
        obj = UserChatStatus.get_by_user(user_id)
        flower_user = FlowerUser.get_by_user(user_id)
        user = User.get(user_id)
        if not obj:
            if not flower_user and chat_status == CHAT_FLOWER_IDENTITY:
                return self.error(FLOWER_USER_INFO_NOT_SET)

            UserChatStatus.add(user_id, chat_status)
        else:
            if not flower_user and chat_status == CHAT_FLOWER_IDENTITY:
                return self.error(FLOWER_USER_INFO_NOT_SET)

            obj.update(chat_status)

        if chat_status == CHAT_FLOWER_IDENTITY:
            rong_client.user_refresh(user_id, flower_user.name, flower_user.avatar_url)
            flower_identity = True
        else:
            rong_client.user_refresh(user_id, user.user_name, user.avatar_url)
            flower_identity = False

        return self.render({
            'status': 0,
            'data': {
                'flower_identity': flower_identity,
            }
        })


class GroupReportHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            reporter_id = self.get_argument('user_id')
            group_id = self.get_argument('group_id')
            reason = self.get_argument('reason', '')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        try:
            Report.add(reporter_id, REPORT_GROUP, group_id, reason)
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'添加举报失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class GroupEnvelopeOpenHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = int(self.get_argument('user_id'))
            envelope_id = self.get_argument('envelope_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        envelope = GroupEnvelope.get(envelope_id)
        if not envelope:
            return self.error(GROUP_ENVELOPE_NOT_FOUND)

        if envelope.receiver_id != user_id:
            return self.error(ACCESS_NOT_ALLOWED)

        if envelope.status == 'C':
            return self.error(GROUP_ENVELOPE_HAS_OPENED)

        try:
            envelope.receive()
        except Exception as e:
            logger.error(u'打开红包失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class GroupMessagePublishHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        group_id = self.get_argument('group_id')
        object_name = self.get_argument('object_name')
        channel_type = self.get_argument('channel_type')
        content = self.get_argument('content')
        message_id = self.get_argument('message_id')
        msg_timestamp = self.get_argument('msg_timestamp')
        msg_timestamp = int(msg_timestamp) / 1000
        create_time = datetime.fromtimestamp(msg_timestamp)

        try:
            GroupMessage.add(message_id, user_id, group_id, object_name, channel_type, content, create_time)
        except Exception as e:
            logger.error(u'添加群聊信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        GroupUser.update_voice_time(group_id, user_id)
        return self.render({
            'status': 0,
        })