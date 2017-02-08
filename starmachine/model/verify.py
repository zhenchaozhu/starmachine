# coding: utf-8

from random import randint
from starmachine.lib.redis_cache import CacheManager
from starmachine import settings
from starmachine.model.consts import REGISTER_VERIFY_CODE_TYPE, RESET_PASSWORD_VERIFY_CODE_TYPE, \
    VALIDATE_VERIFY_CODE_TYPE, WITHDRAW_VERIFY_CODE_TYPE, RESET_PAYMENT_CODE_TYPE, WITHDRAW_ACCOUNT_CODE_TYPE

RegisterVerifyCodeKey = 'register_verify_code:%s'
ResetPasswordVerifyCodeKey = 'reset_password_verify_code:%s'
ValidateVerifyCodeKey = 'validate_verify_code:%s'
WithdrawVerifyCodeKey = 'withdraw_verify_code:%s'
ResetPaymentCodeVerifyCodeKey = 'rest_payment_code_verify_code:%s'
WithdrawAccountVerifyCodeKey = 'withdraw_account_verify_code:%s'
VERIFY_CODE_CACHE_KEY = {
    REGISTER_VERIFY_CODE_TYPE: RegisterVerifyCodeKey,
    RESET_PASSWORD_VERIFY_CODE_TYPE: ResetPasswordVerifyCodeKey,
    VALIDATE_VERIFY_CODE_TYPE: ValidateVerifyCodeKey,
    WITHDRAW_VERIFY_CODE_TYPE: WithdrawVerifyCodeKey,
    RESET_PAYMENT_CODE_TYPE: ResetPasswordVerifyCodeKey,
    WITHDRAW_ACCOUNT_CODE_TYPE: WithdrawAccountVerifyCodeKey,
}

class Verify(object):

    @classmethod
    def add_verify_code(cls, verify_type, telephone, verify_code):
        cache = CacheManager().cache
        key = VERIFY_CODE_CACHE_KEY.get(verify_type) % telephone
        cache.mset({
            key: verify_code,
        })
        cache.expire(key, settings.VERIFY_CODE_EXPIRE_TIME)

    @classmethod
    def get_verify_code(cls, verify_type, telephone):
        cache = CacheManager().cache
        key = VERIFY_CODE_CACHE_KEY.get(verify_type) % telephone
        verify_code = cache.get(key)
        return verify_code

    @classmethod
    def gen_verify_code(cls):
        return randint(100000, 999999)