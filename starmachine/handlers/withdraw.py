# coding: utf-8

import json
import logging
from datetime import datetime
from tornado.web import MissingArgumentError
from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token, createNoncestr
from starmachine.handlers.error import MISSING_PARAMS, ACCOUNT_NOT_FOUND, ACCOUNT_BALANCE_NOT_ENOUGH, SYSTEM_ERROR, \
    USER_NOT_FOUND, MISMATCHED_VERIFY_CODE
from starmachine.model.user import User
from starmachine.model.account import Account
from starmachine.model.withdraw import Withdraw, WithdrawBatch, WithdrawAccount
from starmachine.model.alipay import build_trans_notify_url
from starmachine.model.verify import Verify
from starmachine.model.consts import WITHDRAW_ACCOUNT_CODE_TYPE

logger = logging.getLogger(__name__)

class WithdrawAccountHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        withdraw_accounts = WithdrawAccount.gets_by_user(user_id, start, count)
        return self.render({
            'status': 0,
            'data': [account.jsonify() for account in withdraw_accounts],
        })

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        name = self.get_argument('name')
        account_name = self.get_argument('account_name')
        verify_code = self.get_argument('verify_code')
        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if verify_code != str(Verify.get_verify_code(WITHDRAW_ACCOUNT_CODE_TYPE, user.telephone)):
            return self.error(MISMATCHED_VERIFY_CODE)

        try:
            account = WithdrawAccount.add(user_id, name, account_name)
        except Exception as e:
            logger.error(u'创建提现账号失败')
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': account.jsonify() if account else {},
        })

class WithdrawHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            # withdraw_account_id = self.get_argument('withdraw_account_id')
            withdraw_account = self.get_argument('withdraw_account')
            amount = float(self.get_argument('amount'))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        account = Account.get_by_user(user_id)
        if not account:
            return self.error(ACCOUNT_NOT_FOUND)

        if amount > float(account.balance):
            return self.error(ACCOUNT_BALANCE_NOT_ENOUGH)

        try:
            Withdraw.add(user_id, withdraw_account, amount)
        except Exception as e:
            logger.error(u'提交提现申请失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': {
                'balance': Account.get_by_user(user_id).jsonify().get('balance'),
            }
        })


class WithdrawHandleHandler(APIBaseHandler):

    def post(self):
        try:
            withdraw_ids = self.get_argument('withdraw_ids')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        withdraw_ids = json.loads(withdraw_ids)
        create_time = datetime.now()
        detail_data = ''
        batch_fee = 0
        batch_num = len(withdraw_ids)
        batch_no = create_time.strftime('%Y%m%d%H%M%S') + createNoncestr(5)
        for withdraw_id in withdraw_ids:
            withdraw = Withdraw.get(withdraw_id)
            withdraw_account = withdraw.withdraw_account
            detail_data += '%s^%s^%s^%s^%s' % (withdraw.id, withdraw_account.account_name, withdraw_account.name, withdraw.amount, u'提现')
            batch_fee += float(withdraw.amount)
            withdraw.pending()

        WithdrawBatch.add(batch_no, withdraw_ids, create_time)
        trans_url = build_trans_notify_url(detail_data, batch_no, str(batch_num), str(batch_fee), create_time)
        return self.render({
            'status': 0,
            'data': {
                'trans_url': trans_url,
            }
        })