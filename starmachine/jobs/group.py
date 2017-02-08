# coding: utf-8

import random
from rq.decorators import job
from starmachine.worker import conn
from starmachine.lib.query import DbManager
from starmachine.model.notify import Notify
from starmachine.model.group_user import GroupUser
from starmachine.lib.utils import random_pick
from starmachine.model.PushNotification import push_client
from starmachine.model.consts import CHAT_RED_ENVELOPE, CHAT_MELON_SEEDS, NOTIFY_ACTION_CHAT_ENVELOPE_REWARD, \
    NOTIFY_ACTION_CHAT_ENVELOPE_AST, NOTIFY_ACTION_CHAT_SEEDS_REWARD, NOTIFY_ACTION_CHAT_SEEDS_AST
from starmachine.model.group_envelope import GroupEnvelope, GroupReward
from starmachine.model.group_seeds import GroupSeeds
from starmachine.model.rong import UserChatStatus
from starmachine.model.flower_user import FlowerUser


@job('default', connection=conn)
def chat_user_reward(receiver, helper, group_id, message_id, liked_count):
    if not GroupReward.has_get_reward(group_id, message_id, liked_count):
        rewards = [CHAT_RED_ENVELOPE, CHAT_MELON_SEEDS]
        probability = [0.1, 0.9]
        reward = random_pick(rewards, probability)
        GroupReward.add(receiver.id, group_id, message_id, liked_count, reward)
        if UserChatStatus.is_flower_identity(receiver.id):
            receiver_name = FlowerUser.get_by_user(receiver.id).name
        else:
            receiver_name = receiver.user_name
        if not isinstance(receiver_name, unicode):
            receiver_name = receiver_name.decode('utf-8')

        if UserChatStatus.is_flower_identity(helper.id):
            helper_name = FlowerUser.get_by_user(helper.id).name
        else:
            helper_name = helper.user_name
        if not isinstance(helper_name, unicode):
            helper_name = helper_name.decode('utf-8')

        if reward == CHAT_RED_ENVELOPE:
            amount = random.randint(1, 10) / 100.0
            envelope = GroupEnvelope.add(receiver.id, group_id, message_id, liked_count, amount)
            reward_id = envelope.id
            if int(helper.id) == int(receiver.id):
                Notify.add(helper.id, receiver.id, NOTIFY_ACTION_CHAT_ENVELOPE_REWARD, envelope.id, extra_info=u'呦！您集齐%s个赞召唤出1个红包' % liked_count)
            else:
                Notify.add(helper.id, receiver.id, NOTIFY_ACTION_CHAT_ENVELOPE_REWARD, envelope.id, extra_info=u'呦！您集齐%s个赞召唤出1个红包' % liked_count)
                Notify.add(receiver.id, helper.id, NOTIFY_ACTION_CHAT_ENVELOPE_AST, envelope.id, extra_info=u'牛！助攻成功，您帮%s集齐%s个赞召唤出了1个红包' % (receiver_name, liked_count))
        else:
            amount = 1
            seeds = GroupSeeds.add(receiver.id, group_id, message_id, liked_count, amount)
            reward_id = seeds.id
            if int(helper.id) == int(receiver.id):
                Notify.add(helper.id, receiver.id, NOTIFY_ACTION_CHAT_SEEDS_REWARD, seeds.id, extra_info=u'呦!您集齐了%s个赞召唤出了1枚炒瓜子' % liked_count)
            else:
                Notify.add(helper.id, receiver.id, NOTIFY_ACTION_CHAT_SEEDS_REWARD, seeds.id, extra_info=u'呦!您集齐了%s个赞召唤出了1枚炒瓜子' % liked_count)
                Notify.add(receiver.id, helper.id, NOTIFY_ACTION_CHAT_SEEDS_AST, seeds.id, extra_info=u'牛！助攻成功！您帮%s集齐%s个赞召唤除了八卦必备神器“一枚炒瓜子”' % (receiver_name, liked_count))

        receiver_obj = {
            'id': receiver.id,
            'name': receiver_name,
        }
        helper_obj = {
            'id': helper.id,
            'name': helper_name,
        }
        push_client.notify_chat_reward(receiver_obj, helper_obj, reward, reward_id, amount, liked_count)