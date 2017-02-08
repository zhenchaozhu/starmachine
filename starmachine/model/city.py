# coding: utf-8

from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.province import Province
from starmachine.lib.utils import redis_cache_obj

CITY_CACHE_KEY = 'city:%s'

class City(object):

    table = 'city'

    def __init__(self, id=None, province_id=None, name=None, name_en=None):
        self.id = id
        self.province_id = province_id
        self.name = name
        self.name_en = name_en

    def __repr__(self):
        return '<City:id=%s>' % (self.id)

    @property
    def province(self):
        return Province.get(self.province_id)

    @classmethod
    def add(cls, province_id, name, name_en):
        db = DbManager().db
        sql = 'insert into {table} (province_id, name, name_en) values (%s, %s, %s)'.format(table=cls.table)
        city_id = db.execute(sql, province_id, name, name_en)
        return city_id and cls.get(city_id)

    @classmethod
    @redis_cache_obj(CITY_CACHE_KEY)
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        city_info = db.get(sql, id)
        return city_info and cls(**city_info)

    @classmethod
    def get_by_name(cls, name):
        db = DbManager().db
        sql = 'select * from {table} where name=%s'.format(table=cls.table)
        city_info = db.get(sql, name)
        return city_info and cls(**city_info)

    @classmethod
    def exists_city(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None

    def jsonify(self):
        return {
            'id': self.id,
            'province_name': self.province.name,
            'name': self.name,
            'name_en': self.name_en,
        }
