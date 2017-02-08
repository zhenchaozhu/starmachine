# coding: utf-8

from rq.decorators import job

from starmachine import settings
from starmachine.worker import conn
from starmachine.model.room_push import RoomPush
from starmachine.model.user import User
from starmachine.model.notify import Notify
from starmachine.model.consts import NOTIFY_ACTION_BE_FOLLOWED, NOTIFY_ACTION_CHANGE_PASSWORD, NOTIFY_ACTION_CHANGE_PAYMENT_CODE

@job('default', connection=conn)
def add_content_like(content_id, content_type, user_id):
    from starmachine.model.content.content_like import ContentLiked
    ContentLiked.add_mysql(content_id, content_type, user_id)

@job('default', connection=conn)
def delete_conetnt_like(content_id, content_type, user_id):
    from starmachine.model.content.content_like import ContentLiked
    ContentLiked.delete_from_mysql(content_id, content_type, user_id)

@job('default', connection=conn)
def add_room_user(room_id, user_id, join_time, user_status):
    from starmachine.model.room_user import RoomUser
    RoomUser.add_to_mysql(room_id, user_id, join_time, user_status)

@job('default', connection=conn)
def job_delete_room_user(room_id, user_id):
    from starmachine.model.room_user import RoomUser
    RoomUser.delete_room_user_from_sql(room_id, user_id)

# 推送内容
@job('default', connection=conn)
def push_room_content(room, content, text, start_time):
    from starmachine.model.PushNotification import push_client
    room_push = RoomPush.add(room.creator_id, room.id, content.id)
    push_client.push_room_content(room, content, text, start_time, room_push)

@job('default', connection=conn)
def notify_be_followed(user_id, follow_id):
    user = User.get(user_id)
    user_name = user.name
    if not isinstance(user_name, unicode):
        user_name = user_name.decode('utf-8')

    text = u'%s关注了您' % user_name
    Notify.add(user_id, follow_id, NOTIFY_ACTION_BE_FOLLOWED, None, extra_info=text)

@job('default', connection=conn)
def notify_change_password(user_id, change_time):
    change_time = '%s日%s时%s分' % (change_time.date().strftime('%Y-%m-%d'), change_time.hour, change_time.minute)
    text = u'您于%s修改了登陆密码，如是本人修改无须理会。' % change_time
    Notify.add(user_id, user_id, NOTIFY_ACTION_CHANGE_PASSWORD, None, extra_info=text)

@job('default', connection=conn)
def notify_change_payment_code(user_id, change_time):
    change_time = '%s日%s时%s分' % (change_time.date().strftime('%Y-%m-%d'), change_time.hour, change_time.minute)
    text = u'您于%s修改了支付密码，如是本人修改无须理会。' % change_time
    Notify.add(user_id, user_id, NOTIFY_ACTION_CHANGE_PAYMENT_CODE, None, extra_info=text)

