# coding: utf-8

from starmachine.handlers.base import BaseHandler


class WxEditorHandler(BaseHandler):

    def get(self):
        return self.render('editor/wx_editor.html')

class WxEditorRegisterHandler(BaseHandler):

    def get(self):
        return self.render('editor/register.html')

class RegisterHandler(BaseHandler):

    def get(self):
        return self.render('editor/register.html')

    def post(self):
        email = self.get_argument('user_name')
        password = self.get_argument('password')
