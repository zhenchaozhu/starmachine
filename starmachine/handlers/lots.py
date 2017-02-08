# coding: utf-8

from tornado.web import MissingArgumentError
from starmachine.lib.utils import check_access_token
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS
from starmachine.model.lots import Lots, DrawLots
from starmachine.jobs.integral import handle_daily_draw_lots

class UserDrawLotsHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        lots = Lots.get_random_lots()
        DrawLots.add(user_id, lots.id)
        handle_daily_draw_lots.delay(user_id)
        return self.render({
            'stats': 0,
            'data': lots.jsonify(),
        })