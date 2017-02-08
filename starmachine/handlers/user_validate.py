# coding: utf-8

import json
import logging
from tornado.web import MissingArgumentError
from starmachine.lib.utils import check_access_token
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, USER_NOT_VALIDATED, MISMATCHED_VERIFY_CODE, \
    USER_ALREADY_VALIDATED, SYSTEM_ERROR, OPERATE_NOT_EFFECT
from starmachine.model.consts import VALIDATED_STATUS, VALIDATE_VERIFY_CODE_TYPE, VALIDATE_FAILED_STATUS, VALIDATING_STATUS
from starmachine.model.verify import Verify
from starmachine.model.user import User
from starmachine.model.user_validate import UserValidate
from starmachine.jobs.integral import handle_complete_validate_integral

logger = logging.getLogger(__name__)

class UserValidateHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        user_validate_info = UserValidate.get_by_user_id(user_id)
        if not user_validate_info:
            return self.error(USER_NOT_VALIDATED)
        return self.render({
            'status': 0,
            'data': user_validate_info.jsonify() if user_validate_info else {},
        })

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
            telephone = self.get_argument('telephone')
            id_card = self.get_argument('id_card')
            id_card_front = self.get_argument('id_card_front', '')
            id_card_back = self.get_argument('id_card_back', '')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        user_validate_info = UserValidate.get_by_user_id(user_id)
        if user_validate_info and user_validate_info.status == VALIDATED_STATUS:
            return self.error(USER_ALREADY_VALIDATED)

        id_card_front_url = json.loads(id_card_front)
        if isinstance(id_card_front_url, list):
            id_card_front_url = id_card_front_url[0]

        id_card_back_url = json.loads(id_card_back)
        if isinstance(id_card_back_url, list):
            id_card_back_url = id_card_back_url[0]

        try:
            if not user_validate_info:
                user_validate = UserValidate.add(user_id, name, telephone, id_card, id_card_front_url, id_card_back_url)
            else:
                if user_validate_info.status == VALIDATE_FAILED_STATUS:
                    user_validate = user_validate_info.update(user_id=user_id, name=name, telephone=telephone, id_card=id_card,
                        id_card_front=id_card_front_url, id_card_back=id_card_back_url, reason='', status=VALIDATING_STATUS)
                else:
                    user_validate = user_validate_info
        except Exception as e:
            logger.error(u'添加或更新用户验证信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': user_validate.jsonify(),
        })


class UserValidateNotifyHandler(APIBaseHandler):

    # @check_access_token
    def post(self):
        try:
            user_validate_id = self.get_argument('user_validate_id')
            operate = self.get_argument('operate')
            reason = self.get_argument('reason', '')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        # user = User.get(user_id)
        # if not user:
        #     return self.error(USER_NOT_FOUND)

        user_validate = UserValidate.get(user_validate_id)
        if not user_validate:
            return self.error(USER_NOT_VALIDATED)

        if operate == 'pass':
            user_validate.notify_validate_pass(reason)
            handle_complete_validate_integral.delay(user_validate.user_id)
        elif operate == 'reject':
            user_validate.notify_validate_reject(reason)
        else:
            return self.error(OPERATE_NOT_EFFECT)

        return self.render({
            'status': 0
        })
