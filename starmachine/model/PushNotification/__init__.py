# coding: utf-8

import json
from starmachine.model.device import Device
from starmachine.model.user import User
from starmachine.model.room_user import RoomUser
from starmachine.umpns.umpns_client import um_ios_client, um_android_client
from starmachine.gtpns.gtpns_client import gtpns_client
from starmachine.model.consts import IOS_DEVICE, ANDROID_DEVICE, PUSH_UNICAST_TYPE, PUSH_LISTCAST_TYPE, \
    VALIDATED_STATUS, VALIDATE_FAILED_STATUS, CHAT_RED_ENVELOPE, CHAT_MELON_SEEDS, PUSH_ACTION_GROUP_REWARD

split_arr = lambda A, n=200: [A[i:i+n] for i in range(0, len(A), n)]

class PushClient(object):

    def push_room_content(self, room, content, text, start_time, room_push):
        try:
            ticker = u'事大：【%s】%s' % (room.name.decode('utf-8'), text)
            title = u'事大'
            text = u'【%s】%s' % (room.name.decode('utf-8'), text)
            room_member_ids = RoomUser.get_user_ids_by_room(room.id)
            ios_device_tokens = []
            android_device_tokens = []
            for member_id in room_member_ids:
                device = Device.get_by_user(member_id)
                if not device:
                    continue
                os = int(device.os)
                if os == IOS_DEVICE:
                    ios_device_tokens.append(device.device_token)
                elif os == ANDROID_DEVICE:
                    android_device_tokens.append(device.device_token)

            # 友盟的listcast device_token要求不超过500个device_token
            ios_device_tokens_arr = split_arr(ios_device_tokens, 500)
            # android_device_tokens_arr = split_arr(android_device_tokens, 500)
            info = {
                'content_id': content.id,
                'push_type': PUSH_LISTCAST_TYPE,
                'room_id': room.id,
                'content_type': content.content_type,
            }
            for ios_device_tokens in ios_device_tokens_arr:
                ios_device_token_str = ','.join(ios_device_tokens)
                um_ios_client.push_listcast(ios_device_token_str, text, info, start_time=start_time)

            template = gtpns_client.notificationTemplate(title, text, transContent=json.dumps(info), transType=2)
            # template = gtpns_client.transmissionTemplate(transContent=json.dumps(info), transType=2)
            gtpns_client.pushMessageToList(template, android_device_tokens)
            # for android_device_tokens in android_device_tokens_arr:
            #     android_device_tokens_str = ','.join(android_device_tokens)
            #     um_android_client.push_listcast(android_device_tokens_str, ticker, title, text, info, start_time=start_time)

            room_push.complete()
            return True
        except Exception as e:
            print e
            room_push.fail()
            raise

    def notify_content_like(self, content):
        receiver = content.creator
        device = Device.get_by_user(receiver.id)
        info = {
            'content_id': content.id,
            'push_type': PUSH_UNICAST_TYPE,
            'room_id':  content.room_id,
            'content_type': content.content_type,
        }
        ticker = u'事大：您收到了新赞'
        title = u'事大'
        text = u'您收到了新赞'
        self.push_user_message(device, ticker, title, text, info)

    def notify_comment(self, receiver, content):
        device = Device.get_by_user(receiver.id)
        info = {
            'content_id': content.id,
            'room_id': content.room_id,
            'push_type': PUSH_UNICAST_TYPE,
            'content_type': content.content_type,
        }
        ticker = u'事大：有人评论了您'
        title = u'事大'
        text = u'有人评论了您'
        self.push_user_message(device, ticker, title, text, info)

    def notify_reward(self, content):
        receiver = content.creator
        device = Device.get_by_user(receiver.id)
        info = {
            'content_id': content.id,
            'room_id': content.room_id,
            'push_type': PUSH_UNICAST_TYPE,
            'content_type': content.content_type,
            'balance': float(receiver.account.balance),
        }
        ticker = u'事大：您有一笔新打赏'
        title = u'事大'
        text = u'您有一笔新打赏'
        self.push_user_message(device, ticker, title, text, info)

    def notify_chat_reward(self, receiver, helper, reward, reward_id, amount, liked_count):
        receiver_id = receiver.get('id')
        helper_id = helper.get('id')
        device = Device.get_by_user(receiver_id)
        helper_device = Device.get_by_user(helper_id)
        info = {
            'receiver': {
                'id': receiver_id,
                'name': receiver.get('name'),
            },
            'helper': {
                'id': helper_id,
                'name': helper.get('name'),
            },
            'reward_type': reward,
            'push_type': PUSH_UNICAST_TYPE,
            'action': PUSH_ACTION_GROUP_REWARD,
            'amount': amount,
            'is_assist': False,
            'liked_count': liked_count,
        }
        if reward == CHAT_RED_ENVELOPE:
            info.update({
                'envelop_id': reward_id,
            })
            ticker = u'事大：您收到一枚红包'
            text = u'您收到一枚红包'
            helper_ticker = u'事大：您助攻一枚红包'
            helper_text = u'您助攻一枚红包'
        else:
            ticker = u'事大：您收到一颗瓜子'
            text = u'您收到一颗瓜子'
            helper_ticker = u'事大：您助攻一颗瓜子'
            helper_text = u'您助攻一颗瓜子'

        title = u'事大'
        if int(receiver_id) == int(helper_id):
            self.push_user_message_transmission(device, ticker, title, text, info)
        else:
            self.push_user_message_transmission(device, ticker, title, text, info)
            info['is_assist'] = True
            self.push_user_message_transmission(helper_device, helper_ticker, title, helper_text, info)

    def push_user_message(self, device, ticker, title, text, info):
        if not device:
            return False

        os = int(device.os)

        if os == IOS_DEVICE:
            um_ios_client.push_unicast(device.device_token, text, extra=info)
        elif os == ANDROID_DEVICE:
            template = gtpns_client.notificationTemplate(title, text, transType=2, transContent=json.dumps(info))
            # template = gtpns_client.transmissionTemplate(transContent=json.dumps(info), transType=2)
            gtpns_client.pushMessageToSingle(template, device.device_token)

        return True

    def push_user_message_transmission(self, device, ticker, title, text, info):
        if not device:
            return False

        os = int(device.os)

        if os == IOS_DEVICE:
            um_ios_client.push_unicast(device.device_token, text, extra=info)
        elif os == ANDROID_DEVICE:
            # template = gtpns_client.notificationTemplate(title, text, transType=2, transContent=json.dumps(info))
            template = gtpns_client.transmissionTemplate(transContent=json.dumps(info), transType=2)
            gtpns_client.pushMessageToSingle(template, device.device_token)

        return True

    def push_validate_status(self, user_validate):
        device = Device.get_by_user(user_validate.user_id)
        if not device:
            return False

        info = {
            'user_validate': user_validate.jsonify(),
            'push_type': 3
        }
        if user_validate.status == VALIDATED_STATUS:
            ticker = u'事大：您通过了状态验证'
            title = u'事大'
            text = u'恭喜您身份验证已通过，可以去发起活动或提现啦！'
        elif user_validate.status == VALIDATE_FAILED_STATUS:
            ticker = u'事大：您通过了状态验证'
            title = u'事大'
            text = u'对不起，您的身份验证未通过，请重新提交准确无误的身份验证资料。'
        else:
            return False

        self.push_user_message(device, ticker, title, text, info)


push_client = PushClient()
