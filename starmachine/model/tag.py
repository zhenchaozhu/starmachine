# coding: utf-8

from datetime import datetime

from starmachine.lib.query import DbManager
from starmachine.lib.utils import redis_cache_obj
from starmachine.model.consts import TAG_TYPE_STAR

TAG_CACHE_KEY = 'tag:%s'

class Tag(object):

    table = 'tag'

    def __init__(self, id=None, name=None, source=None, type=None, create_time=None, update_time=None):
        self.id = id
        self.name = name
        self.source = source
        self.type = type
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Tag:id=%s>' % (self.id)

    @classmethod
    def add(cls, tag_name, source, type=TAG_TYPE_STAR):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (name, source, type, create_time) values (%s, %s, %s, %s)'.format(table=cls.table)
        tag_id = db.execute(sql, tag_name, source, type, create_time)
        return tag_id

    @classmethod
    @redis_cache_obj(TAG_CACHE_KEY)
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        tag_info = db.get(sql, id)
        return  tag_info and cls(**tag_info)

    @classmethod
    def exists_tag(cls, tag_name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, tag_name)[0]
        except:
            return None

    @classmethod
    def get_by_name(cls, tag_name):
        db = DbManager().db
        sql = 'select * from {table} where name=%s'.format(table=cls.table)
        tag_info = db.get(sql, tag_name)
        return tag_info and cls(**tag_info)

    @classmethod
    def get_random_list(cls, count=6):
        db = DbManager().db
        sql = 'select * from {table} as t1 join(select round(rand() * ((select max(id) from {table}) - ' \
            '(select min(id) from {table})) + (select min(id) from {table})) as id) as t2 where ' \
            't1.id >= t2.id ORDER BY t1.id LIMIT 1'.format(table=cls.table)
        rst = set()
        while len(rst) < count:
            id = int(db.get(sql).get('id'))
            rst.add(id)
        tlist = []
        for r in rst:
            tag = Tag.get(r)
            tlist.append(tag)
        return tlist

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        infos = db.query(sql)
        return [cls(**info) for info in infos]

    def jsonify(self):
        return {
            'id': self.id,
            'name': self.name,
            'source': self.source,
            'type': self.type,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                            self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        }