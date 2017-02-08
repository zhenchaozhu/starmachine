# coding: utf-8

import json
import time
from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.handlers.base import BaseHandler, APIBaseHandler
from starmachine.model.xiaoshuo import XiaoShuo, XiaoShuoFocusPic
from starmachine.model.group import Group
from starmachine.model.group_message_liked import GroupMessage
from starmachine.model.user import User
from starmachine.model.flower_user import FlowerUser
from starmachine.model.rong import UserChatStatus

class IndexHandler(BaseHandler):

    def get(self):
        return self.render('index.html')

    def head(self):
        self.write('star428')


class AdvertiseHandler(BaseHandler):

    def get(self):
        return self.render('advertise.html')


class RegistrationClauseHandler(BaseHandler):

    def get(self, *args, **kwargs):
        return self.render('registration_clause.html')


class XiaoShuoHandler(BaseHandler):

    def get(self):
        focus_pic = XiaoShuoFocusPic.get_focus_pic()
        articles = XiaoShuo.gets_all()
        data = {
            'focus_pic': focus_pic,
            'articles': articles,
        }
        return self.render('xiaoshuo.html', **data)


class GroupHotMessagePageHandler(BaseHandler):

    def get(self, group_id):
        share_timestamp = self.get_argument('share_time', '')
        group = Group.get(group_id)
        if not group:
            return self.render('group/404.html')

        if share_timestamp:
            delta = int(time.time()) - int(share_timestamp)
            if delta > 24 * 60 * 60:
                return self.render('group/404.html')

        hot_messages = GroupMessage.get_hot_messages(group_id, 20)
        messages = []
        for message in hot_messages:
            content = json.loads(message.content)
            creator_id = message.creator_id
            flower_identity = UserChatStatus.is_flower_identity(creator_id)
            if flower_identity:
                flower_user = FlowerUser.get_by_user(creator_id)
                user_name = flower_user.user_name
                avatar = flower_user.avatar_url
            else:
                user = User.get(creator_id)
                user_name = user.user_name
                avatar = user.avatar_url

            if not avatar:
                avatar = 'http://pic.star428.com/group/img/portrait.png'
            if not user_name:
                user_name = u'冰冰女生'
            create_time = message.create_time.strftime('%H:%M')
            liked_amount = int(message.liked_amount)
            messages.append({
                "avatar": avatar,
                "user_name": user_name,
                'create_time': create_time,
                'liked_amount': liked_amount,
                'content': content,
                'object_name': message.object_name,
            })


        data = {
            'messages': messages,
            'group': group,
        }
        return self.render('group/hot_message.html', **data)