# -*- coding: utf-8 -*-
__author__ = 'wei'

import hashlib
import time
import urllib2
import json
import base64
import os
import threading
import thread
from starmachine.gtpns.igetui.igt_message import *


class IGeTui:
    def __init__(self, host, appKey, masterSecret):
        self.host = host
        self.appKey = appKey
        self.masterSecret = masterSecret
        self.serviceMap = {}
        self.flag = 0
        #print str(time.time())+self.host
        if self.host==None or len(self.host)<=0:
            hosts=self.getConnOSServerHostList()
            #print hosts
        else:
            hosts=[]
            hosts.append(host.strip())
        self.getFastest(hosts)
        
    def getConnOSServerHostList(self):
        l=self.serviceMap.get(self.appKey)
        if l!=None and len(l)!=0:
            return l
        l = self.getConfigOsServerHostList()
        if l==None or len(l)==0:
            l=["http://sdk.open.api.igexin.com/serviceex",
                "http://sdk.open.api.gepush.com/serviceex", 
                "http://sdk.open.api.getui.net/serviceex"]
            l.sort()
            self.serviceMap[self.appKey]=l
            return self.serviceMap.get(self.appKey)
        l.sort()
        return l
    
    def getConfigOsServerHostList(self):
        url = 'http://sdk.open.apilist.igexin.com/os_list' 
        f = urllib2.urlopen(url) 
        data = f.read() 
        l=data.split("\r\n")
        ll=[]
        for line in l:
            if line!="" and line.startswith('http'):
                ll.append(line)
        return ll

    def testurl(self,no,url):
        try:
            r = urllib2.urlopen(urllib2.Request(url),timeout=3)
            if self.flag == 0:
                self.flag=1
                self.host= url
            else:
                thread.exit()
        except:
            #print "timeout"
            pass
        
    def fast(self,hosts):
        k={}
        for i in range(len(hosts)):
            k[i]=threading.Thread(target=self.testurl,args=(1,hosts[i]))
            k[i].setDaemon(True)
            k[i].start()
        while self.flag == 0:
            time.sleep(0.000000001)
        self.flag=0
        print self.host
        #thread.exit()

    def getFastest(self,hosts):
        if len(hosts)==0:
            raise ValueError("can't get fastest host from empty list")
        elif len(hosts)==1:
            self.host = hosts[0]
        else:
            try:
                self.getCycleInspect(hosts)               
            except:
                pass
        
    def getCycleInspect(self,hosts):
        try:
            self.fast(hosts)
            t=threading.Timer(600,self.getCycleInspect,args=[hosts])
            t.setDaemon(True)
            t.start()
        except:
            pass
    
    def connect(self):
        timenow = self.getCurrentTime()
        sign = self.getSign(self.appKey, timenow, self.masterSecret)
        params = {}
        params['action'] = 'connect'
        params['appkey'] = self.appKey
        params['timeStamp'] = timenow
        params['sign'] = sign
        rep = self.httpPost(params)
        if 'success' == (rep['result']):
            return True

        print rep
        raise Exception(str(rep) + "appKey or masterSecret is auth failed.")

    def pushMessageToSingle(self, message, target):
        params = {}
        params['action'] = "pushMessageToSingleAction"
        params['appkey'] = self.appKey
        transparent = message.data.getTransparent()
        params['clientData'] = base64.encodestring(transparent.SerializeToString())
        params['transmissionContent'] = message.data.transmissionContent
        params['isOffline'] = message.isOffline
        params['offlineExpireTime'] = message.offlineExpireTime
        # 增加pushNetWorkType参数(0:不限;1:wifi;2:4G/3G/2G)
        params["pushNetWorkType"] = message.pushNetWorkType
        params['appId'] = target.appId
        params['clientId'] = target.clientId
        params['alias'] = target.alias
        params['type'] = 2 #default is message
        params['pushType'] = message.data.pushType
        return self.httpPostJson(params)

    def pushAPNMessageToSingle(self, appId, deviceToken, message):
        params = {}
        params['action'] = "apnPushToSingleAction"
        params['appId'] = appId
        params['appkey'] = self.appKey
        params['DT'] = deviceToken
        params['PI'] = base64.encodestring(message.data.pushInfo.SerializeToString())

        return self.httpPostJson(params)

    def pushMessageToApp(self, message, taskGroupName=None):
        params = {}
        contentId = self.getContentId(message, taskGroupName)
        params['action'] = "pushMessageToAppAction"
        params['appkey'] = self.appKey
        params['contentId'] = contentId
        params['type'] = 2
        return self.httpPostJson(params)
        # transparent = message.data.getTransparent()
        # params['clientData'] = base64.encodestring(transparent.SerializeToString())
        # params['transmissionContent'] = message.data.transmissionContent
        # params['isOffline'] = message.isOffline
        # params['offlineExpireTime'] = message.offlineExpireTime
        # params['appIdList'] = message.appIdList
        # params['phoneTypeList'] = message.phoneTypeList
        # params['provinceList'] = message.provinceList
        # params['type'] = 2 # default is message
        # params['pushType'] = message.data.pushType
        # params['tagList'] = message.tagList

        

    def pushMessageToList(self, contentId, targets):
        params = {}
        params['action'] = 'pushMessageToListAction'
        params['appkey'] = self.appKey
        params['contentId'] = contentId
        needDetails = os.getenv("needDetails", "false")
        params['needDetails'] = needDetails
        targetList = []
        for target in targets:
            appId = target.appId
            clientId = target.clientId
            alias = target.alias
            target = {"appId": appId, "clientId": clientId, "alias": alias}
            targetList.append(target)

        params['targetList'] = targetList
        params['type'] = 2
        return self.httpPostJson(params)

    def pushAPNMessageToList(self, appId, contentId, deviceTokenList):
        params = {}
        params['action'] = "apnPushToListAction"
        params['appkey'] = self.appKey
        params['appId'] = appId
        params['contentId'] = contentId
        params['DTL'] = deviceTokenList
        needDetails = os.getenv("needDetails", "false")
        params['needDetails'] = needDetails

        return self.httpPostJson(params)


    def stop(self, contentId):
        params = {}
        params['action'] = 'stopTaskAction'
        params['appkey'] = self.appKey
        params['contentId'] = contentId

        ret = self.httpPostJson(params)
        if ret["result"] == 'ok':
            return True
        return False

    def getClientIdStatus(self, appId, clientId):
        params = {}
        params['action'] = 'getClientIdStatusAction'
        params['appkey'] = self.appKey
        params['appId'] = appId
        params['clientId'] = clientId

        return self.httpPostJson(params)



    def bindAlias(self, appId, alias, clientId):
        params = {}
        params['action'] = 'alias_bind'
        params['appkey'] = self.appKey
        params['appid'] = appId
        params['alias'] = alias
        params['cid'] = clientId

        return self.httpPostJson(params)

    def bindAliasBatch(self, appId, targetList):
        params = {}
        aliasList = []
        for target in targetList:
            user = {}
            user['cid'] = target.clientId
            user['alias'] = target.alias
            aliasList.append(user)

        params['action'] = 'alias_bind_list'
        params['appkey'] = self.appKey
        params['appid'] = appId
        params['aliaslist'] = aliasList

        return self.httpPostJson(params)

    def queryClientId(self, appId, alias):
        params = {}
        params['action'] = "alias_query"
        params['appkey'] = self.appKey
        params['appid'] = appId
        params['alias'] = alias

        return self.httpPostJson(params)

    def queryAlias(self, appId, clientId):
        params = {}
        params['action'] = "alias_query"
        params['appkey'] = self.appKey
        params['appid'] = appId
        params['cid'] = clientId

        return self.httpPostJson(params)

    def unBindAlias(self, appId, alias, clientId=None):
        params = {}
        params['action'] = "alias_unbind"
        params['appkey'] = self.appKey
        params['appid'] = appId
        params['alias'] = alias

        if clientId is not None and clientId.strip() != "":
            params['cid'] = clientId
        return self.httpPostJson(params)

    def unBindAliasAll(self, appId, alias):
        return self.unBindAlias(appId, alias, None)

    def getContentId(self, message, taskGroupName=None):
        params = {}

        if taskGroupName is not None and taskGroupName.strip() != "":
            if len(taskGroupName) > 40:
                raise Exception("TaskGroupName is OverLimit 40")
            params['taskGroupName'] = taskGroupName

        params['action'] = "getContentIdAction"
        params['appkey'] = self.appKey
        transparent = message.data.getTransparent()
        params['clientData'] = base64.encodestring(transparent.SerializeToString())
        params['transmissionContent'] = message.data.transmissionContent
        params["isOffline"] = message.isOffline
        params["offlineExpireTime"] = message.offlineExpireTime
        # 增加pushNetWorkType参数(0:不限;1:wifi;2:4G/3G/2G)
        params["pushNetWorkType"] = message.pushNetWorkType
        params["pushType"] = message.data.pushType
        params['type'] = 2

        if isinstance(message, IGtAppMessage):
            params['speed'] = message.speed

        if isinstance(message, IGtListMessage):
            params['contentType'] = 1
        else:
            params['contentType'] = 2
            params['appIdList'] = message.appIdList
            params['phoneTypeList'] = message.phoneTypeList
            params['provinceList'] = message.provinceList
            params['tagList'] = message.tagList

        ret = self.httpPostJson(params)

        return ret['contentId'] if ret['result'] == 'ok' else ' '

    def getAPNContentId(self, appId, message):
        params = {}
        params['action'] = "apnGetContentIdAction"
        params['appkey'] = self.appKey
        params['appId'] = appId
        params['PI'] = base64.encodestring(message.data.pushInfo.SerializeToString())

        ret = self.httpPostJson(params)
        return ret['contentId'] if ret['result'] == 'ok' else ''

    def cancelContentId(self, contentId):
        params = {}
        params['action'] = 'cancleContentIdAction'
        params['contentId'] = contentId
        ret = self.httpPostJson(params)
        return True if ret['result'] == 'ok' else False

    def getCurrentTime(self):
        return (int)(time.time() * 1000)

    def getSign(self, appKey, timeStamp, masterSecret):
        rawValue = appKey + str(timeStamp) + masterSecret
        return hashlib.md5(rawValue.encode()).hexdigest()

    def httpPostJson(self, params):
        params['version'] = '3.0.0.0'
        ret = self.httpPost(params)
        if ret is not None and "sign_error" == ret["result"]:
            self.connect()
            ret = self.httpPost(params)
        return ret

    def httpPost(self, params):
        #如果通过代理访问我们接口，需要自行配置代理，示例如下：
        #opener = urllib2.build_opener(urllib2.ProxyHandler({'http':'192.168.1.108:808'}), urllib2.HTTPHandler(debuglevel=1))
        #urllib2.install_opener(opener)
        data_json = json.dumps(params)
        req = urllib2.Request(self.host, data_json)
        retry_time_limit = 3
        isFail = True
        tryTime = 0
        while isFail and tryTime < retry_time_limit:
            try:
                res_stream = urllib2.urlopen(req, timeout=60)
                isFail = False
            except:
                isFail = True
                tryTime += 1
                print("try " + str(tryTime) + " time failed, time out.")

        page_str = res_stream.read()
        page_dict = eval(page_str)
        return page_dict

    def getPushResult(self,taskId):
        params={}
        params["action"]="getPushMsgResult"
        params["appkey"]=self.appKey
        params["taskId"]=taskId
        try:
            return self.httpPostJson(params)
        except Exception,e:
            print "host"+self.host+"getPushResult失败"+str(e)
        
        
    def getUserTags(self,appId,clientId):
        params={}
        params["action"] = "getUserTags"
        params["appkey"] = self.appKey
        params["appId"] = appId
        params["clientId"] = clientId
        try:
            return self.httpPostJson(params)
        except Exception,e:
            print "host"+self.host+"getUserTags失败"+str(e)
    
    def  setClientTag(self,appId,clientId,tags):
        params={}
        params["action"] = "setTagAction"
        params["appkey"] = self.appKey
        params["appId"] = appId
        params["clientId"] = clientId
        params["tagList"] = tags
        try:
            return self.httpPostJson(params)
        except Exception,e:
            print "host"+self.host+"setTag失败"+str(e)
        





























