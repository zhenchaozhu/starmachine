# coding: utf-8

from rq.decorators import job
from starmachine.worker import conn
from starmachine.model.consts import ROOM_USER_CREATOR, ROOM_USER_ADMIN, NOTIFY_ACTION_ROOM_REMOVED, NOTIFY_ACTION_ROOM_SILENT
from starmachine.model.notify import Notify

@job('default', connection=conn)
def room_remove_user_notify(operator, operator_status, room, remove_user):
    room_name = room.name
    operator_name = operator.name
    if not isinstance(room_name, unicode):
        room_name = room_name.decode('utf-8')

    if not isinstance(operator_name, unicode):
        operator_name = operator_name.decode('utf-8')

    if operator_status == ROOM_USER_CREATOR:
        text = u'对不起，您已经被房主%s移除出房间%s，不能再加入该房间了。' % (operator_name, room_name)
    else:
        text = u'对不起，您已经被房管%s移除出房间%s，不能再加入该房间了。' % (operator_name, room_name)

    Notify.add(operator.id, remove_user.id, NOTIFY_ACTION_ROOM_REMOVED, room.id, extra_info=text)

@job('default', connection=conn)
def room_silent_user_notify(operator, operator_status, room, silent_user):
    operator_name = operator.name
    if not isinstance(operator_name, unicode):
        operator_name = operator_name.decode('utf-8')

    if operator_status == ROOM_USER_CREATOR:
        text = u'对不起，您已经被房主%s操作禁言，禁言24H后方可发布内容。' % operator_name
    else:
        text = u'对不起，您已经被房管%s操作禁言，禁言24H后方可发布内容。' % operator_name

    Notify.add(operator.id, silent_user.id, NOTIFY_ACTION_ROOM_SILENT, room.id, extra_info=text)