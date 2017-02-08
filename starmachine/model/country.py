# coding: utf-8

from starmachine.lib.query import DbManager
from starmachine.lib.utils import redis_cache_obj

COUNTRY_CACHE_KEY = 'country:%s'

class Country(object):

    table = 'country'

    def __init__(self, id=None, name=None, name_en=None):
        self.id = id
        self.name = name
        self.name_en = name_en

    def __repr__(self):
        return '<Country:id=%s>' % self.id

    @classmethod
    def add(cls, name, name_en):
        db = DbManager().db
        sql = 'insert into {table} (name, name_en) values (%s, %s)'.format(table=cls.table)
        country_id = db.execute(sql, name, name_en)
        return country_id and cls.get(country_id)

    @classmethod
    @redis_cache_obj(COUNTRY_CACHE_KEY)
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        country_info = db.get(sql, id)
        return country_info and cls(**country_info)

    @classmethod
    def get_by_name(cls, name):
        db = DbManager().db
        sql = 'select * from {table} where name=%s'.format(table=cls.table)
        country_info = db.get(sql, name)
        return country_info and cls(**country_info)

    @classmethod
    def exists_country(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None

    def jsonify(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
        }