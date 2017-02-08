# coding: utf-8

import logging
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.tag import Tag
from starmachine.model.consts import USER_TAG_CACHE_KEY, TAG_USER_CACHE_KEY

logger = logging.getLogger(__name__)

class UserTag(object):

    table = 'user_tag'

    def __init__(self, id=None, user_id=None, tag_id=None):
        self.id = id
        self.user_id = user_id
        self.tag_id = tag_id

    def __repr__(self):
        return '<UserTag:id=%s>' % (self.id)

    @classmethod
    def add(cls, user_id, tag_ids):
        db = DbManager().db
        sql = 'insert into {table} (user_id, tag_id) values (%s, %s)'.format(table=cls.table)
        try:
            for tag_id in tag_ids:
                db.execute(sql, user_id, tag_id)
            logger.info(u'添加用户标签关系成功。')
        except Exception as e:
            logger.error(u'添加用户标签关系失败。Error:[%s]' % e)
            raise

        return

    @classmethod
    def update_tags(cls, user_id, tag_ids):
        db = DbManager().db
        delete_sql = 'delete from {table} where user_id=%s'.format(table=cls.table)
        db.execute(delete_sql, user_id)
        for tag_id in tag_ids:
            sql = 'insert into {table} (user_id, tag_id) values (%s, %s)'.format(table=cls.table)
            db.execute(sql, user_id, tag_id)
        return

    @classmethod
    def delete(cls, user_id, tag_id):
        db = DbManager().db
        sql = 'delete from {table} where user_id=%s and tag_id=%s'.format(table=cls.table)
        db.execute(sql, user_id, tag_id)
        return

    @classmethod
    def get_tags_by_user(cls, user_id):
        db = DbManager().db
        sql = 'select tag_id from {table} where user_id=%s'.format(table=cls.table)
        tag_ids_dict = db.query(sql, user_id)
        if tag_ids_dict:
            return [Tag.get(tag_id_dict.get('tag_id')) for tag_id_dict in tag_ids_dict]
        else:
            return []

    @classmethod
    def exists_tag(cls, user_id, tag_id):
        db = DbManager().db
        sql = 'select id from {table} where user_id=%s and tag_id=%s'.format(table=cls.table)
        try:
            return db.query(sql, user_id, tag_id)[0]
        except:
            return False