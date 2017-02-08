# coding: utf-8

import torndb
from starmachine import settings

_mysql_server = {}
MYSQL_SERVER = settings.MYSQL_SERVER

for key in MYSQL_SERVER.keys():
    sql_info = MYSQL_SERVER[key]
    _mysql_server[key] = torndb.Connection(sql_info.get('host'), sql_info.get('database'),
                    sql_info.get('user'), sql_info.get('password'), charset = "utf8mb4")

class DbManager(object):

    def __init__(self, server='default'):
        self.db = _mysql_server[server]

db = DbManager().db
