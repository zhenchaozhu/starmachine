# coding: utf-8

from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS, USER_NOT_FOUND, SYSTEM_ERROR, DEVICE_NOT_FOUND
from starmachine.lib.utils import check_access_token
from starmachine.model.user import User
from starmachine.model.device import Device
from starmachine.model.consts import ANDROID_DEVICE, IOS_DEVICE, OTHER_DEVICE

class DeviceHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            device_token = str(self.get_argument('device_token'))
        except:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if len(device_token) == 32:
            os = ANDROID_DEVICE
        elif len(device_token) == 64:
            os = IOS_DEVICE
        else:
            os = OTHER_DEVICE

        device = Device.get_by_user(user_id)
        if not device:
            device = Device.add(user_id, device_token, os)
        elif (str(device.device_token) != device_token or int(device.os) != os):
            device.update_device_token(device_token, os)

        if not device:
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': device.jsonify()
        })

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        device = Device.get_by_user(user_id)
        if not device:
            return self.error(DEVICE_NOT_FOUND)

        return self.render({
            'status': 0,
            'data': device.jsonify()
        })

    @check_access_token
    def delete(self):
        user_id = self.get_argument('user_id')
        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        device = Device.get_by_user(user_id)
        if not device:
            return self.error(DEVICE_NOT_FOUND)

        device.delete()
        return self.render({
            'status': 0,
        })