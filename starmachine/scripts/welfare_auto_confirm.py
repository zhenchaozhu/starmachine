# coding: utf-8

from datetime import datetime
from starmachine.model.order.welfare_order import WelfareOrder
from starmachine.jobs.welfare import welfare_confirm_notify
from starmachine.model.user import User
from starmachine.model.content.welfare import Welfare

auto_confirm_seconds = 10 * 24 * 3600
now = datetime.now()
welfare_confirm_orders = WelfareOrder.gets_delivery_orders()
for welfare_confirm_order in welfare_confirm_orders:
    delivery_time = welfare_confirm_order.delivery_time
    if now - delivery_time >= auto_confirm_seconds:
        welfare = Welfare.get(welfare_confirm_order.welfare_id)
        user = User.get(welfare_confirm_order.user_id)
        welfare_confirm_order.confirm()
        welfare_confirm_notify.delay(welfare, user)
