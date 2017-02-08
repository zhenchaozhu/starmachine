# coding: utf-8

import os
import tornado.ioloop
import tornado.autoreload
import tornado.web
from tornado.options import define, options, parse_command_line
from starmachine import settings
from starmachine.log import init_log

def release():
    from starmachine.lib.query import _mysql_server
    for key in _mysql_server:
        db = _mysql_server[key]
        db.close()

def init_settings():
    # 加载环境配置项
    define('port', default=8080, type=int, help=u'监听端口')
    define("log_dir", default='/tmp', type=str, help=u'日志目录')
    define('profile', default='local', type=str, help=u'运行配置')

    parse_command_line()
    settings.init(options.profile, options.log_dir, options.port)
    init_log(options.log_dir)
    return options

def start_application():
    from starmachine.url import urls

    application_settings = {
        'handlers': urls,
        'debug': settings.DEBUG,
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    }
    application = tornado.web.Application(**application_settings)

    print 'server on port %s' % settings.PORT
    print 'server log on %s' % settings.LOG_DIR
    print 'server profile: %s' % settings.Profile.current_name

    application.listen(settings.PORT)
    io_loop = tornado.ioloop.IOLoop.instance()

    #这段代码是解决mysql因为tornado重启连接没有断开的问题
    tornado.autoreload.add_reload_hook(release)
    tornado.autoreload.start(io_loop)

    io_loop.start()

def run():
    init_settings()
    start_application()

if __name__ == '__main__':
    run()