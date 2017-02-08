# coding: utf-8

MYSQL_SERVER = {
    'default': {
        'host': '123.57.46.53',
        'database': 'starmachine',
        'user': 'root',
        'password': 'starMachine2015',
    },
    'write': {
        'host': '123.57.46.53',
        'database': 'starmachine',
        'user': 'root',
        'password': 'starMachine2015',
    },
    'read': {
        'host': '123.57.46.53',
        'database': 'starmachine',
        'user': 'root',
        'password': 'starMachine2015',
    }
}
REDIS_HOST = '123.57.46.53'
REDIS_PORT = 6379
DEBUG = True
CACHE_SERVERS = {
    'default': ('123.57.46.53', 6379),
}
VERIFY_CODE_EXPIRE_TIME = 15* 60
IMAGE_TYPE_LIST = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
HOST = 'http://develop.star428.com'
BUCKET = 'starmachine'
DOMAIN_HOST_ALI = 'http://pic-test.star428.com/'
DOMAIN_HOST_QINIU = 'http://7xj2qd.com2.z0.glb.qiniucdn.com/'
OPEN_SEARCH_INDEX = 'develop_starmachine_room'
RONGCLOUD_APP_KEY = "mgb7ka1nb5t5g"
RONGCLOUD_APP_SECRET = "PekV64dB1ZN"