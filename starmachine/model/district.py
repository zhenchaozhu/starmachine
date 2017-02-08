# coding: utf-8

from starmachine.lib.query import db

class District(object):

    table = 'district'

    def __init__(self, id=None, city_id=None, name=None, name_en=None):
        self.id = id
        self.city_id = city_id
        self.name = name
        self.name_en = name_en

    def __repr__(self):
        return '<District:id=%s>' % (self.id)

    @classmethod
    def add(cls, city_id, name, name_en):
        sql = 'insert into {table} (city_id, name, name_en) values (%s, %s, %s)'.format(table=cls.table)
        db.execute(sql, city_id, name, name_en)

    @classmethod
    def get_by_name(cls, name):
        sql = 'select * from {table} where name=%s'.format(table=cls.table)
        district_info = db.get(sql, name)
        return district_info and cls(**district_info)

    @classmethod
    def exists_district(cls, name):
        sql = 'select id from {table} where name=%s'.format(table=cls.table)
        try:
            return db.query(sql, name)[0]
        except:
            return None
