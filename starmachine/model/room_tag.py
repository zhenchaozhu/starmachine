# coding: utf-8

import logging
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.room import Room
from starmachine.model.tag import Tag
from starmachine.model.consts import ROOM_TAG_CACHE_KEY, TAG_ROOM_CACHE_KEY

logger = logging.getLogger(__name__)

class RoomTag(object):

    table = 'room_tag'

    def __init__(self, id=None, room_id=None, tag_id=None):
        self.id = id
        self.room_id = room_id
        self.tag_id = tag_id

    def __repr__(self):
        return '<RoomTag:id=%s>' % (self.id)

    @classmethod
    def add(cls, room_id, tag_ids):
        db = DbManager().db
        sql = 'insert into {table} (room_id, tag_id) values (%s, %s)'.format(table=cls.table)
        try:
            for tag_id in tag_ids:
                db.execute(sql, room_id, tag_id)
            logger.info(u'添加房间标签关系成功。')
        except Exception as e:
            logger.error(u'添加房间标签关系失败。Error:[%s]' % e)
            raise

        return

    @classmethod
    def delete(cls, room_id, tag_id):
        db = DbManager().db
        sql = 'delete from {table} where room_id=%s and tag_id=%s'.format(table=cls.table)
        try:
            db.execute(sql, room_id, tag_id)
            logger.info(u'删除房间标签关系成功。')
        except Exception as e:
            logger.error(u'删除房间标签关系失败。Error:[%s]' % e)
            raise

        return

    @classmethod
    def update_tags(cls, room_id, tag_ids):
        db = DbManager().db
        delete_sql = 'delete from {table} where room_id=%s'.format(table=cls.table)
        db.execute(delete_sql, room_id)
        for tag_id in tag_ids:
            sql = 'insert into {table} (room_id, tag_id) values (%s, %s)'.format(table=cls.table)
            db.execute(sql, room_id, tag_id)
        return

    @classmethod
    def get_tag_ids_by_room(cls, room_id):
        db = DbManager().db
        sql = 'select tag_id from {table} where room_id=%s'.format(table=cls.table)
        tag_ids_dict = db.query(sql, room_id)
        return tag_ids_dict and [tag_id_dict.get('tag_id') for tag_id_dict in tag_ids_dict]

    @classmethod
    def get_tags_by_room(cls, room_id):
        db = DbManager().db
        sql = 'select tag_id from {table} where room_id=%s'.format(table=cls.table)
        tag_ids_dict = db.query(sql, room_id)
        if tag_ids_dict:
            return [Tag.get(tag_id_dict.get('tag_id')) for tag_id_dict in tag_ids_dict]
        else:
            return []

    @classmethod
    def get_rooms_by_tags(cls, tags):
        db = DbManager().db
        params = ['tag_id=%s' % tag.id for tag in tags if tag]
        union_str = ' or '.join(params)
        if union_str:
            sql = 'select room_id from {table} where %s'.format(table=cls.table) % union_str
            room_ids_dict = db.query(sql)
            room_ids = [room_id_dict.get('room_id') for room_id_dict in room_ids_dict]
            room_ids = list(set(room_ids))
            return room_ids and [Room.get(room_id) for room_id in room_ids]

        return []

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        infos = db.query(sql)
        return [cls(**info) for info in infos]