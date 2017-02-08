# coding: utf-8

from starmachine.gtpns.igt_push import *
from igetui.template import *
from igetui.template.igt_base_template import *
from igetui.template.igt_transmission_template import *
from igetui.template.igt_link_template import *
from igetui.template.igt_notification_template import *
from igetui.template.igt_notypopload_template import *
from igetui.template.igt_apn_template import *
from igetui.igt_message import *
from igetui.igt_target import *
from igetui.template import *

#toList接口每个用户返回用户状态开关,true：打开 false：关闭
os.environ['needDetails'] = 'true'
APPKEY = "RYYztb227D60RbErPNdol8"
APPID = "mDjAyZH0RQ6rb3063BWMd2"
MASTERSECRET = "gQILXHR8ij7ONLvoXXNQP8"
HOST = 'http://sdk.open.api.igexin.com/apiex.htm'


class GtpnsClient(object):

    def __init__(self, host, appId, appKey, masterSecret):
        self.push = IGeTui(host, appKey, masterSecret)
        self.host = host
        self.appId = appId
        self.appKey = appKey
        self.masterSecret = masterSecret

    def pushMessageToSingle(self, template, device_token):
        message = IGtSingleMessage()
        message.data = template
        message.isOffline = True
        message.offlineExpireTime = 1000 * 3600 * 12

        target = Target()
        target.appId = self.appId
        target.clientId = device_token

        ret = self.push.pushMessageToSingle(message, target)
        print ret
        return ret

    def pushMessageToList(self, template, device_tokens):
        message = IGtListMessage()
        message.data = template
        message.isOffline = True
        message.offlineExpireTime = 1000 * 3600 * 12

        targets = list()
        for device_token in device_tokens:
            target = Target()
            target.appId = self.appId
            target.clientId = device_token
            targets.append(target)

        contentId = self.push.getContentId(message)
        ret = self.push.pushMessageToList(contentId, targets)
        print ret
        return ret

    def notificationTemplate(self, text, title='', transType=1, transContent='', logo='', logoURL='', isRing=True, isVibrate=True, isClearable=True):
        template = NotificationTemplate()
        template.appId = self.appId
        template.appKey = self.appKey
        template.transmissionType = transType
        template.transmissionContent = transContent
        template.title = title
        template.text = text
        template.logo = logo
        template.logoURL = logoURL
        template.isRing = isRing
        template.isVibrate = isVibrate
        template.isClearable = isClearable
        # iOS 推送需要的PushInfo字段 前三项必填，后四项可以填空字符串
        # template.setPushInfo(actionLocKey, badge, message, sound, payload, locKey, locArgs, launchImage)
        #template.setPushInfo("open",4,"message","","","","","");
        return template

    def transmissionTemplate(self, transContent, transType=1):
        template = TransmissionTemplate()
        template.transmissionType = transType
        template.appId = self.appId
        template.appKey = self.appKey
        template.transmissionContent = transContent
        # iOS 推送需要的PushInfo字段 前三项必填，后四项可以填空字符串
        #template.setPushInfo(actionLocKey, badge, message, sound, payload, locKey, locArgs, launchImage)
        #template.setPushInfo("",2,"","","","","","")
        return template


gtpns_client = GtpnsClient(
    host = HOST,
    appId = APPID,
    appKey = APPKEY,
    masterSecret = MASTERSECRET,
)


