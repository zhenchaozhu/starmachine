# coding: utf-8

import logging
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token
from starmachine.model.advice import Advice
from starmachine.handlers.error import SYSTEM_ERROR

logger = logging.getLogger(__name__)


class AdviceHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        text = self.get_argument('text')
        reply_user_id = self.get_argument('reply_user_id')
        try:
            Advice.add(user_id, reply_user_id, text)
        except Exception as e:
            logger.error(u'提交或回复建议失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class UserAdviceListHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        advices = Advice.get_advices_by_user(user_id, start, count)
        return self.render({
            'status': 0,
            'data': [advice.jsonify() for advice in advices],
        })