# coding: utf-8

from rq.decorators import job
from starmachine.worker import conn
from starmachine.model.notify import Notify
from starmachine.model.room_user import RoomUser
from starmachine.model.consts import  NOTIFY_ACTION_WELFARE_CREATED, NOTIFY_ACTION_WELFARE_ROBED, NOTIFY_ACTION_WELFARE_END,\
    NOTIFY_ACTION_WELFARE_ORDERED, NOTIFY_ACTION_WELFARE_CONFIRMED, WELFARE_ORDER_DELIVER
from starmachine.model.order.welfare_order import WelfareOrder

def welfare_end_notify(welfare):
    welfare.welfare_robed_end()
    robed_users = WelfareOrder.get_robed_users_by_welfare(welfare.id)
    welfare_name = welfare.name
    if not isinstance(welfare_name, unicode):
        welfare_name = welfare_name.decode('utf-8')

    if len(welfare_name) > 10:
        welfare_name = welfare_name[:10] + u'……'

    text = u'"%s"抢福利已结束，小事儿在吭哧吭哧确认订单中！' % welfare_name
    for user in robed_users:
        Notify.add(welfare.creator_id, user.id, NOTIFY_ACTION_WELFARE_END, welfare.id, extra_info=text)

def welfare_auto_complete(welfare_order):
    welfare_order = WelfareOrder.get(welfare_order.id)
    if welfare_order.status == WELFARE_ORDER_DELIVER:
        welfare_order.confirm()

@job('default', connection=conn)
def welfare_created_notify(room, welfare):
    user_ids = RoomUser.get_user_ids_by_room(room.id)
    welfare_name = welfare.name
    if not isinstance(welfare_name, unicode):
        welfare_name = welfare_name.decode('utf-8')

    if len(welfare_name) > 10:
        welfare_name = welfare_name[:10] + u'……'

    room_name = room.name
    if not isinstance(room_name, unicode):
        room_name = room_name.decode('utf-8')

    text = u'%s房间发福利啦："%s"' % (room_name, welfare_name)
    for user_id in user_ids:
        Notify.add(welfare.creator_id, user_id, NOTIFY_ACTION_WELFARE_CREATED, welfare.id, extra_info=text)

@job('default', connection=conn)
def welfare_robed_notify(user, welfare):
    text = u'呼啦啦，恭喜神枪手，已顺利抢到福利！小事儿会在抢福利结束后1-3个工作日确认福利订单！'
    Notify.add(welfare.creator_id, user.id, NOTIFY_ACTION_WELFARE_ROBED, welfare.id, extra_info=text)

@job('default', connection=conn)
def welfare_ordered_notify(welfare, welfare_order, platform=None, order_num=None):
    # welfare_orders = WelfareOrder.gets_by_welfare(welfare.id)
    # robed_users = WelfareOrder.get_robed_users_by_welfare(welfare.id)
    welfare_name = welfare.name
    if len(welfare_name) > 10:
        welfare_name = welfare_name[:10] + u'……'

    if not isinstance(welfare_name, unicode):
        welfare_name = welfare_name.decode('utf-8')

    text = u'"%s"已经下单啦' % (welfare_name)
    Notify.add(welfare.creator_id, welfare_order.user_id, NOTIFY_ACTION_WELFARE_ORDERED, welfare.id, extra_info=text)
    # for welfare_order in welfare_orders:
    #     welfare_order.delivery()
    #     Notify.add(welfare.creator_id, welfare_order.user_id, NOTIFY_ACTION_WELFARE_ORDERED, welfare.id, extra_info=text)

@job('default', connection=conn)
def welfare_confirm_notify(welfare, user):
    welfare_name = welfare.name
    if not isinstance(welfare_name, unicode):
        welfare_name = welfare_name.decode('utf-8')

    if len(welfare_name) > 10:
        welfare_name = welfare_name[:10] + u'……'

    text = u'"%s"已收货完成，小事儿祝您下次继续抢到单哦。' % welfare_name
    Notify.add(welfare.creator_id, user.id, NOTIFY_ACTION_WELFARE_CONFIRMED, welfare.id, extra_info=text)