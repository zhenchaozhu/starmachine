# coding: utf-8

MYSQL_SERVER = {
    'default': {
        'host': 'rdsoakhu8cgwzowpnpzle.mysql.rds.aliyuncs.com',
        'database': 'starmachine',
        'user': 'starmachine',
        'password': 'starmachine',
    },
    'write': {
        'host': 'rdsoakhu8cgwzowpnpzle.mysql.rds.aliyuncs.com',
        'database': 'starmachine',
        'user': 'starmachine',
        'password': 'starmachine',
    },
    'read': {
        'host': 'rdsoakhu8cgwzowpnpzle.mysql.rds.aliyuncs.com',
        'database': 'starmachine',
        'user': 'starmachine',
        'password': 'starmachine',
    }
}
DEBUG = False
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
CACHE_SERVERS = {
    'default': ('127.0.0.1', 6379),
}
VERIFY_CODE_EXPIRE_TIME = 15* 60
IMAGE_TYPE_LIST = ['image/gif', 'image/jpeg', 'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png']
HOST = 'https://www.star428.com'
BUCKET = 'star428'
IMAGE_DOMAIN = 'http://pic.star428.com/'
OPEN_SEARCH_INDEX = 'starmachine_room'
RONGCLOUD_APP_KEY = "8w7jv4qb7khky"
RONGCLOUD_APP_SECRET = "dxA8S1H4yXw"