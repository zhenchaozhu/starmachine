# coding: utf-8

from starmachine.handlers.base import APIBaseHandler
from starmachine.lib.utils import check_access_token
from starmachine.model.group import Group

class GroupHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        name = self.get_argument('name')
        announcement = self.get_argument('announcement', '')
        avatar = self.get_argument('avatar', '')
        group = Group.add(user_id, avatar, name, announcement)

