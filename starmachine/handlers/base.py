# coding: utf-8

import json
import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        x_real_ip = self.request.headers.get("X-Real-IP")
        self.remote_ip = self.request.remote_ip if not x_real_ip else x_real_ip

    def render(self, template_name, **kwargs):
        super(BaseHandler, self).render(template_name, **kwargs)


class APIBaseHandler(BaseHandler):
    """API基类，返回JSON格式的数据"""

    def error(self, error):
        error = self.error_to_dict(error)
        # self.set_status(error.get('status_code'))
        self.render(error)

    def error_to_dict(self, error):
        return {
            'status': error[0],
            'msg': error[1],
            'status_code': error[2],
            'source': error[3],
        }

    def set_api_header(self):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        # TODO 这个将来如果跨域可能会用到
        #origin = self.request.headers.get('Origin')
        #valid_origin = re.compile('^http://(\w+\.)*m\.sohu\.com(:\d+)?$')
        #if origin and self.valid_origin.match(origin):
        #    self.set_header('Access-Control-Allow-Origin', origin)

    def pre_render(self):
        self.set_api_header()

    def render(self, data):
        self.pre_render()
        if isinstance(data, dict):
            data = json.dumps(data)

        self.write(data)
        if not self._finished:
            self.finish()


