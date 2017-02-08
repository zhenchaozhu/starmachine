# coding: utf-8

from starmachine.lib.query import DbManager
from starmachine.model.country import Country

class Province(object):

    table = 'province'

    def __init__(self, id=None, country_id=None, name=None, name_en=None):
        self.id = id
        self.country_id = country_id
        self.name = name
        self.name_en = name_en

    def __repr__(self):
        return '<Province:id=%s>'

    @property
    def country(self):
        return Country.get(self.country_id)

    @classmethod
    def add(cls, country_id, name, name_en):
        db = DbManager().db
        sql = 'insert into {table} (country_id, name, name_en) values (%s, %s, %s)'.format(table=cls.table)
        province_id = db.execute(sql, country_id, name, name_en)
        return province_id and cls.get(province_id)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        province_info = db.get(sql, id)
        return province_info and cls(**province_info)

    @classmethod
    def get_by_name(cls, name):
        db = DbManager().db
        sql = 'select * from {table} where name=%s'.format(table=cls.table)
        province_info = db.get(sql, name)
        return province_info and cls(**province_info)

    @classmethod
    def exists_province(cls, name):
        db = DbManager().db
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None

    def jsonify(self):
        return {
            'id': self.id,
            'country_name': self.country.name,
            'name': self.name,
            'name_en': self.name_en
        }



