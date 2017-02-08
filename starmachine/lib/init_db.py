#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from subprocess import Popen, PIPE


DEFAULT_CONFIG = {
    'db': 'starmachine',
    'user': 'root',
    'password': 'zzc',
    'host': '127.0.0.1',
    'port': 3306,
}

try:
    from config import MYSQL_CONFIG
    config = MYSQL_CONFIG
except ImportError:
    config = DEFAULT_CONFIG


if __name__ == '__main__':
    db = config['db']
    user = config['user']
    passwd = config['password']
    # filename = 'database/database.sql'
    filename = '/Users/apple/workspace/starmachine/dbstructure/woleyi.sql'
    process = Popen('mysql %s -u%s -p%s' % (db, user, passwd), stdout=PIPE,
                    stdin=PIPE, shell=True)
    output = process.communicate('source ' + filename)[0]
