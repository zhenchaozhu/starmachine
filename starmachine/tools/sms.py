# coding: utf-8

from rq.decorators import job
from starmachine.worker import conn
from starmachine.lib.sms import send_sms
from starmachine.model.consts import REGISTER_VERIFY_CODE_TYPE, RESET_PASSWORD_VERIFY_CODE_TYPE

@job('default', connection=conn)
def send_register_verify_code_sms(phone, verify_code):
    msg = '【事大app】您的验证码是%s（15分钟内有效，如您已经完成操作，请忽略此条信息）' % verify_code
    send_sms(phone, msg)