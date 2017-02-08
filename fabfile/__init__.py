# coding: utf-8

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

from fabric.state import env

# from essay.tasks import build
# from essay.tasks import deploy
from essay.tasks import nginx
from .deploy import deploy, deploy_rq
# from .build import build
import build

env.GIT_SERVER = 'https://bitbucket.org/'  # ssh地址只需要填：github.com
env.PROJECT = 'starmachine'
env.BUILD_PATH = '/opt/deploy/'
env.PROJECT_OWNER = 'zhenchaozhu'
env.DEFAULT_BRANCH = 'master'
env.PYPI_INDEX = 'http://123.57.46.53:3141/simple/'
env.NGINX_BIN = '/usr/sbin/nginx'
env.NGINX_CONF = '/etc/nginx/nginx.conf'

######
# deploy settings:
env.PROCESS_COUNT = 4  #部署时启动的进程数目
env.roledefs = {
    'build': ['root@123.57.46.53'],  # 打包服务器配置
    'develop': [
        'root@123.57.46.53'
    ], # 测试服务器
    'product': [
        'root@101.200.172.105'
    ], # 正式服务器
    'nginx': [
        'root@101.200.172.105'
    ]
}
env.VENV_PORT_PREFIX_MAP = {
    'a': '1215',
    'b': '1216',
}

env.VIRTUALENV_PREFIX = '/opt/www/starmachine'
env.SUPERVISOR_CONF_TEMPLATE = os.path.join(PROJECT_ROOT, 'conf', 'supervisord.conf')

env.RQ_PATH = '/var/rq/starmachine'
env.RQ_SUPERVISOR_CONF_TEMPLATE = os.path.join(PROJECT_ROOT, 'conf/rq', 'supervisord.conf')
