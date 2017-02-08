# coding: utf-8
from os import path
import logging.config

def init_log(log_dir, debug=False):
    if not path.exists(log_dir):
        print 'log path is not exist:%s' % log_dir
        exit(-1)

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(levelname)s %(asctime)s %(module)s:%(funcName)s:%(lineno)d %(message)s'
            },
            'simple': {
                'format': '%(level)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': path.join(log_dir, 'starmachine.log'),
                'maxBytes': 1024 * 1024 * 50,
                'backupCount': 5,
                'formatter': 'default',
            },
        },
        'loggers': {
            'starmachine': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }

    logging.config.dictConfig(config)

    # TODO: 后期可以加上sentry管理项目bug
    # tornado adds RotateFileHandler & StreamHandler into root logger
    # so we cannot add SentryHandler using dictConfig
    # if debug is False:
    #     from raven.handlers.logging import SentryHandler
    #     udp_url = 'udp://b4ed10d35f4a4598b9d26d909c994a28:8912e4c65c294d3aba9d4378f3c598e6@10.13.81.171:9001/2'
    #     sentry = SentryHandler(udp_url)
    #     sentry.setLevel(logging.ERROR)
    #     root = logging.getLogger()
    #     root.addHandler(sentry)
    #     front = logging.getLogger('starmachine')
    #     front.addHandler(sentry)
