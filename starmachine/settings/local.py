# coding: utf-8

MYSQL_SERVER = {
    'default': {
        'host': '127.0.0.1',
        'database': 'starmachine',
        'user': 'root',
        'password': 'zzc',
    },
    'write': {
        'host': '127.0.0.1',
        'database': 'starmachine',
        'user': 'root',
        'password': 'zzc',
    },
    'read': {
        'host': '127.0.0.1',
        'database': 'starmachine',
        'user': 'root',
        'password': 'zzc',
    }
}
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
DEBUG = True
CACHE_SERVERS = {
    'default': ('127.0.0.1', 6379),
}
VERIFY_CODE_EXPIRE_TIME = 15* 60
IMAGE_TYPE_LIST = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
HOST = 'http://127.0.0.1'
BUCKET = 'star428'
IMAGE_DOMAIN = 'http://pic.star428.com/'
RONGCLOUD_APP_KEY = "mgb7ka1nb5t5g"
RONGCLOUD_APP_SECRET = "PekV64dB1ZN"