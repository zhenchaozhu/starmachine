# coding: utf-8

from datetime import datetime
from rq.decorators import job
from starmachine.worker import conn
from starmachine.lib.redis_cache import CacheManager
from starmachine.lib.query import DbManager
from starmachine.model.notify import Notify
from starmachine.model.user_intergal import UserIntegral, UserIntegralRecord
from starmachine.model.consts import USER_DAILY_RECEIVE_LIKE_COUNT, USER_DAILY_VOTE_COUNT, INTEGRAL_MAP, \
    USER_INTEGRAL_FIRST_JOIN_ROOM, USER_INTEGRAL_FIRST_SEND_LIKE, USER_INTEGRAL_FIRST_SET_PAYMENT_CODE, \
    USER_INTEGRAL_FIRST_COMPLETE_VALIDATE, USER_INTEGRAL_FIRST_ROOM_USER_OVER_500, USER_INTEGRAL_DAILY_LOGIN, \
    USER_INTEGRAL_DAILY_CREATE_CONTENT, USER_INTEGRAL_DAILY_DRAW_LOTS, USER_INTEGRAL_DAILY_COMMENT, \
    USER_INTEGRAL_DAILY_VOTE, USER_INTEGRAL_DAILY_GET_LIKED, USER_INTEGRAL_DAILY_SEND_REWARD, USER_INTEGRAL_DAILY_GET_REWARD, \
    USER_INTEGRAL_DAILY_CREATE_WELFARE, USER_INTEGRAL_DAILY_ROB_WELFARE, NOTIFY_ACTION_LEVEL_UP, NOTIFY_ACTION_LEVEL_UP_THREE

user_first_join_room_key = 'user:%s:integral:first_join_room'
user_first_send_like_key = 'user:%s:integral:first_send_like'
user_first_set_payment_code_key = 'user:%s:integral:first_set_payment_code'
user_first_complete_validate_key = 'user:%s:integral:first_complete_validate'
user_first_room_over_500_key = 'user:%s:integral:first_room_over_500'

cache = CacheManager().cache
db = DbManager().db

def add_user_integral(user_id, source, integral, redis_key=None, extra=None):
    db = DbManager().db
    create_time = datetime.now()
    date = create_time.date()
    try:
        db.execute('begin;')
        sql = 'update {table} set integral=integral+%s where user_id=%s'.format(table=UserIntegral.table)
        db.execute(sql, integral, user_id)
        sql = 'select integral from {table} where user_id=%s'.format(table=UserIntegral.table)
        amount = db.get(sql, user_id).get('integral')
        sql = 'insert into {table} (user_id, source, amount, integral, date, create_time, extra) values ' \
        '(%s, %s, %s, %s, %s, %s)'.format(table=UserIntegralRecord.table)
        db.execute(sql, user_id, source, amount, integral, date, create_time, extra)
        db.execute('commit;')
        if redis_key:
            cache.set(redis_key, 1)
    except:
        db.execute('rollback;')
        raise

    level = handle_integral_level_point(integral)
    if level:
        if level == 3:
            text = u'恭喜您有%s积分，升级至LV3啦，赶紧去创建房间和聊天组吧！' % integral
            Notify.add(user_id, user_id, NOTIFY_ACTION_LEVEL_UP_THREE, None, extra_info=text)
        else:
            text = u'恭喜您有%s积分，升级至LV%s啦，查看积分攻略更快升级！' % (integral, level)
            Notify.add(user_id, user_id, NOTIFY_ACTION_LEVEL_UP, None, extra_info=text)

def handle_integral_level_point(integral):
    if integral == 1:
        level = 1
    elif integral == 11:
        level = 2
    elif integral == 31:
        level = 3
    elif integral == 101:
        level = 4
    elif integral == 301:
        level = 5
    elif integral == 601:
        level = 6
    elif integral == 1001:
        level = 7
    elif integral == 2001:
        level = 8
    elif integral == 4001:
        level = 9
    elif integral == 10001:
        level =10
    else:
        return None

    return level

@job('default', connection=conn)
def handle_join_room_integral(user_id, room_id):
    pass
    # redis_key = user_first_join_room_key % user_id
    # integral = INTEGRAL_MAP.get('first_join_room')
    # if not cache.exists(redis_key):
    #     add_user_integral(user_id, USER_INTEGRAL_FIRST_JOIN_ROOM, integral, redis_key, room_id)

@job('default', connection=conn)
def handle_set_payment_code_integral(user_id):
    pass
    # redis_key = user_first_set_payment_code_key % user_id
    # integral = INTEGRAL_MAP.get('first_set_payment_code')
    # if not cache.exists(redis_key):
    #     add_user_integral(user_id, USER_INTEGRAL_FIRST_SET_PAYMENT_CODE, integral, redis_key)

@job('default', connection=conn)
def handle_complete_validate_integral(user_id):
    pass
    # redis_key = user_first_complete_validate_key % user_id
    # integral = INTEGRAL_MAP.get('first_complete_validate')
    # if not cache.exists(redis_key):
    #     add_user_integral(user_id, USER_INTEGRAL_FIRST_COMPLETE_VALIDATE, integral, redis_key)

@job('default', connection=conn)
def handle_room_user_over_500_integral(user_id, room_id):
    pass
    # redis_key = user_first_room_over_500_key % user_id
    # integral = INTEGRAL_MAP.get('first_room_user_over_500')
    # if not cache.exists(redis_key):
    #     add_user_integral(user_id, USER_INTEGRAL_FIRST_ROOM_USER_OVER_500, integral, redis_key, room_id)

@job('default', connection=conn)
def handle_daily_login(user_id):
    pass
    # integral = INTEGRAL_MAP.get('daily_login')
    # if not UserIntegralRecord.daily_login_integral_enough(user_id):
    #     add_user_integral(user_id, USER_INTEGRAL_DAILY_LOGIN, integral)

@job('default', connection=conn)
def handle_daily_create_content(user_id, content_id):
    pass
    # integral = INTEGRAL_MAP.get('daily_create_content')
    # if not UserIntegralRecord.daily_create_content_integral_enough(user_id):
    #     add_user_integral(user_id, USER_INTEGRAL_DAILY_CREATE_CONTENT, integral, extra=content_id)

@job('default', connection=conn)
def handle_daily_draw_lots(user_id, lots_id):
    pass
    # integral = INTEGRAL_MAP.get('daily_draw_lots')
    # if not UserIntegralRecord.daily_draw_lots_integral_enough(user_id):
    #     add_user_integral(user_id, USER_INTEGRAL_DAILY_DRAW_LOTS, integral, extra=lots_id)

@job('default', connection=conn)
def handle_daily_comment(user_id, comment_id):
    pass
    # integral = INTEGRAL_MAP.get('daily_comment')
    # if not UserIntegralRecord.daily_comment_integral_enough(user_id):
    #     add_user_integral(user_id, USER_INTEGRAL_DAILY_COMMENT, integral, extra=comment_id)

@job('default', connection=conn)
def handle_daily_vote_integral(user_id, vote_id):
    pass
    # create_time = datetime.now()
    # date = create_time.date()
    # user_daily_vote_redis_key = USER_DAILY_VOTE_COUNT % (user_id, date)
    # integral = INTEGRAL_MAP.get('daily_vote')
    # if cache.exists(user_daily_vote_redis_key):
    #     vote_count = cache.get(user_daily_vote_redis_key)
    #     if 0 < vote_count % 2 <= 3:
    #         add_user_integral(user_id, USER_INTEGRAL_DAILY_VOTE, integral, extra=vote_id)

@job('default', connection=conn)
def handle_daily_send_like_integral(user_id, receiver_id):
    pass
    # create_time = datetime.now()
    # date = create_time.date()
    # first_send_like_redis_key = user_first_send_like_key % user_id
    # first_like_integral = INTEGRAL_MAP.get('first_send_like')
    # integral = INTEGRAL_MAP.get('first_send_like')
    # user_daily_redis_key = USER_DAILY_RECEIVE_LIKE_COUNT % (receiver_id, date)
    # if not cache.exists(first_like_integral):
    #     add_user_integral(user_id, USER_INTEGRAL_FIRST_SEND_LIKE, integral, first_send_like_redis_key, extra=receiver_id)
    #
    # if cache.exists(user_daily_redis_key):
    #     receive_count = cache.get(user_daily_redis_key)
    #     integral = INTEGRAL_MAP.get('daily_get_like')
    #     if 0 < receive_count % 10 <=10:
    #         add_user_integral(receiver_id, USER_INTEGRAL_DAILY_GET_LIKED, integral, extra=receiver_id)

@job('default', connection=conn)
def handle_daily_send_reward(reward_order):
    pass
    # creator_id = reward_order.creator_id
    # receiver_id = reward_order.receiver_id
    # send_reward_integral = INTEGRAL_MAP.get('daily_send_reward')
    # get_reward_integral = INTEGRAL_MAP.get('daily_receive_reward')
    # if not UserIntegralRecord.daily_send_reward_integral_enough(creator_id):
    #     add_user_integral(creator_id, USER_INTEGRAL_DAILY_SEND_REWARD, send_reward_integral, extra=reward_order.id)
    #
    # if not UserIntegralRecord.daily_get_reward_integral_enough(receiver_id):
    #     add_user_integral(receiver_id, USER_INTEGRAL_DAILY_GET_REWARD, get_reward_integral, extra=reward_order.id)

@job('default', connection=conn)
def handle_daily_create_welfare(user_id, welfare_id):
    pass
    # integral = INTEGRAL_MAP.get('daily_create_welfare')
    # if not UserIntegralRecord.daily_create_welfare_integral_enough(user_id):
    #     add_user_integral(user_id, USER_INTEGRAL_DAILY_CREATE_WELFARE, integral, extra=welfare_id)

@job('default', connection=conn)
def handle_daily_rob_welfare(user_id, welfare_id):
    pass
    # integral = INTEGRAL_MAP.get('daily_rob_welfare')
    # if not UserIntegralRecord.daily_rob_welfare_integral_enough(user_id):
    #     add_user_integral(user_id, USER_INTEGRAL_DAILY_ROB_WELFARE, integral, extra=welfare_id)