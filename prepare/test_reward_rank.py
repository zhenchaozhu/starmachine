# coding: utf-8

from starmachine.lib.redis_cache import CacheManager
from starmachine.model.order.reward_order import RewardOrder
from starmachine.model.consts import USER_REWARD_RANK_CACHE_KEY, ROOM_USER_REWARD_CACHE_KEY
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.content import Content
from starmachine.model.room_user import RoomUser
from starmachine.model.withdraw import Withdraw

reward_orders = RewardOrder.gets_all()
cache = CacheManager().cache
rst = {}
for reward_order in reward_orders:
    if reward_order.status == 'C':
        # amount = float(reward_order.amount) * 100
        redis_key = USER_REWARD_RANK_CACHE_KEY
        # cache.zincrby(redis_key, reward_order.creator_id, amount)
        amount = float(reward_order.amount) * 100
        user_id = reward_order.creator_id
        room_id = reward_order.room_id
        redis_key = ROOM_USER_REWARD_CACHE_KEY % room_id
        cache.zincrby(redis_key, user_id, amount)