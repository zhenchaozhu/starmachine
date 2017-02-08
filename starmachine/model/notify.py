# coding: utf-8

import json
from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import NOTIFY_UNREAD, NOTIFY_READ, NOTIFY_TYPE_LIKED, NOTIFY_TYPE_SYSTEM, NOTIFY_TYPE_REWARD, \
    NOTIFY_TYPE_COMMENT, NOTIFY_ACTION_CONTENT_COMMENT, NOTIFY_ACTION_CONTENT_REWARD, NOTIFY_ACTION_CONTENT_LIKED, \
    NOTIFY_ACTION_COMMENT_REPLY, POSTS_TYPE, NOTIFY_ACTION_CHAT_ENVELOPE_REWARD
from starmachine.model.content import Content
from starmachine.model.comment import Comment
from starmachine.model.user import User
from starmachine.lib.utils import init_pic_url
from starmachine.model.group_envelope import GroupEnvelope

class Notify(object):

    table = 'notify'

    def __init__(self, id=None, sender_id=None, receiver_id=None, action=None, target_id=None, notify_type=None, extra=None,
        extra_info=None, status=None, create_time=None, read_time=None):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.action = action
        self.target_id = target_id
        self.notify_type = notify_type
        self.extra = extra
        self.extra_info = extra_info
        self.status = status
        self.create_time = create_time
        self.read_time = read_time

    def __repr__(self):
        return '<Notify:id=%s>' % (self.id)
        
    @property
    def sender(self):
        if self.sender_id:
            return User.get(self.sender_id)

    @property
    def receiver(self):
        if self.receiver_id:
            return User.get(self.receiver_id)

    @classmethod
    def add(cls, sender_id, receiver_id, action, target_id, notify_type=NOTIFY_TYPE_SYSTEM, extra=None, extra_info=None, status=NOTIFY_UNREAD):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (sender_id, receiver_id, action, target_id, notify_type, extra, extra_info, status, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        notify_id = db.execute(sql, sender_id, receiver_id, action, target_id, notify_type, extra, extra_info, status, create_time)
        return notify_id

    @classmethod
    def get_notifies(cls, user_id, start, count):
        db = DbManager().db
        read_time = datetime.now()
        sql = 'select * from {table} where receiver_id=%s order by create_time desc limit %s, %s'.format(table=cls.table)
        notify_infos = db.query(sql, user_id, start, count)
        sql = 'update {table} set status=%s, read_time=%s where status=%s and receiver_id=%s'.format(table=cls.table)
        db.execute(sql, NOTIFY_READ, read_time, NOTIFY_UNREAD, user_id)
        return notify_infos and [cls(**notify_info) for notify_info in notify_infos]

    @classmethod
    def get_user_unread_notify_count(cls, user_id):
        db = DbManager().db
        sql = 'select count(id) from {table} where receiver_id=%s and status=%s'.format(table=cls.table)
        rst = db.get(sql, user_id, NOTIFY_UNREAD)
        return rst and rst.get('count(id)')

    @classmethod
    def get_user_unread_notify_count_by_type(cls, user_id, notify_type):
        db = DbManager().db
        sql = 'select count(id) from {table} where receiver_id=%s and notify_type=%s and status=%s'.format(table=cls.table)
        rst = db.get(sql, user_id, notify_type, NOTIFY_UNREAD)
        return rst and rst.get('count(id)')

    @classmethod
    def get_user_latest_notify_by_type(cls, user_id, notify_type):
        db = DbManager().db
        sql = 'select * from {table} where receiver_id=%s and notify_type=%s order by create_time desc limit 1'.format(table=cls.table)
        rst = db.get(sql, user_id, notify_type)
        return rst and cls(**rst)

    @classmethod
    def get_notifies_by_type(cls, user_id, notify_type, start=0, count=10):
        """
        根据通知类型获取通知
        """
        db = DbManager().db
        read_time = datetime.now()
        sql = 'select * from {table} where receiver_id=%s and notify_type=%s order by create_time desc limit %s, %s'.format(table=cls.table)
        notify_infos = db.query(sql, user_id, notify_type, start, count)
        sql = 'update {table} set status=%s, read_time=%s where status=%s and receiver_id=%s and notify_type=%s'.format(table=cls.table)
        db.execute(sql, NOTIFY_READ, read_time, NOTIFY_UNREAD, user_id, notify_type)
        return notify_infos and [cls(**notify_info) for notify_info in notify_infos]

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        rst = db.query(sql)
        return rst and [cls(**r) for r in rst]

    def update(self, **kwargs):
        db = DbManager().db
        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        r = db.execute(sql)
        return r

    def jsonify(self):
        action = int(self.action)
        content = Content.get(self.target_id)
        data = {
            'id': self.id,
            'action': action,
            'status': self.status,
            'create_time': self.create_time if isinstance(self.create_time, basestring) else
                            self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'notify_type': self.notify_type,
            'extra': self.extra,
            'extra_info': self.extra_info,
        }
        if content:
            if content.content_type == POSTS_TYPE:
                images = content.jsonify().get('images')
            else:
                images = None
            data.update({
                'room_id': content.room_id,
                'content': {
                    'id': content.id,
                    'content_type': content.content_type,
                    'images': images,
                }
            })

        if self.sender:
            data.update({
                'sender': {
                    'id': self.sender.id,
                    'name': self.sender.user_name,
                    'avatar': self.sender.avatar_url,
                }
            })

        if self.receiver:
            data.update({
                'receiver': {
                    'id': self.receiver.id,
                    'name': self.receiver.user_name,
                    'avatar': self.receiver.avatar_url,
                }
            })

        if action == NOTIFY_ACTION_CONTENT_REWARD:
            data.update({
                'reward_amount': self.extra_info
            })

        if action in (NOTIFY_ACTION_CONTENT_COMMENT, NOTIFY_ACTION_COMMENT_REPLY):
            data.update({
                'comment_text': self.extra_info
            })

        if action == NOTIFY_ACTION_CHAT_ENVELOPE_REWARD:
            envelope = GroupEnvelope.get(self.target_id)
            data.update({
                'envelope': {
                    'id': self.target_id,
                    'status': envelope.status,
                    'amount': float(envelope.amount),
                    'liked_amount': envelope.liked_amount,
                }
            })

        return data

