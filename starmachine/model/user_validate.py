# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.lib.utils import init_pic_url
from starmachine.model.consts import VALIDATED_STATUS, VALIDATE_FAILED_STATUS, VALIDATING_STATUS
from starmachine.tools.postman import push_validate_status

class UserValidate(object):

    table = 'user_validate'

    def __init__(self, id=None, user_id=None, name=None, telephone=None, id_card=None, id_card_front=None,
        id_card_back=None, status=None, reason=None, create_time=None, update_time=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.telephone = telephone
        self.id_card = id_card
        self.id_card_front = id_card_front
        self.id_card_back = id_card_back
        self.status = status
        self.reason = reason
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<UserValidate:id=%s>' % (self.id)

    @classmethod
    def add(cls, user_id, name, telephone, id_card, id_card_front, id_card_back, status=VALIDATING_STATUS, reason=''):
        db = DbManager().db
        create_time = datetime.now()
        sql = 'insert into {table} (user_id, name, telephone, id_card, id_card_front, id_card_back, status, reason, create_time) ' \
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        user_validate_id = db.execute(sql, user_id, name, telephone, id_card, id_card_front, id_card_back, status, reason, create_time)
        return user_validate_id and cls(user_validate_id, user_id, name, telephone, id_card, id_card_front, id_card_back, status, reason, create_time, None)

    @classmethod
    def get(cls, id):
        db = DbManager().db
        sql = 'select * from {table} where id=%s'.format(table=cls.table)
        user_validate_info = db.get(sql, id)
        return user_validate_info and cls(**user_validate_info)

    @classmethod
    def get_by_user_id(cls, user_id):
        db = DbManager().db
        sql = 'select * from {table} where user_id=%s'.format(table=cls.table)
        user_validate_info = db.get(sql, user_id)
        return user_validate_info and cls(**user_validate_info)

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        # start = (page - 1) * size if page > 1 else 0
        # end = page * size - 1
        sql = 'select * from {table} order by id desc'.format(table=cls.table)
        validate_lists = db.query(sql)
        return validate_lists and [cls(**validate) for validate in validate_lists]

    @classmethod
    def amount(cls):
        db = DbManager().db
        sql = 'select count(id) from {table}'.format(table=cls.table)
        count = db.get(sql)
        return count and count.get('count(id)')

    def delete(self):
        db = DbManager().db
        sql = 'delete from {table} where id=%s'.format(table=self.table)
        db.execute(sql, self.id)

    def update(self, **kwargs):
        db = DbManager().db
        if 'update_time' not in kwargs:
            kwargs.update({'update_time': datetime.now()})

        params = ['%s="%s"' % (key, kwargs.get(key)) for key in kwargs]
        update_sql = ', '.join(params)
        sql = 'update {table} set %s where id=%s'.format(table=self.table) % (update_sql, self.id)
        db.execute(sql)
        return self.get(self.id)

    def notify_validate_pass(self, reason=''):
        push_validate_status.delay(self)

    def notify_validate_reject(self, reason=''):
        push_validate_status.delay(self)

    def jsonify(self):
        from starmachine.model.user import User
        user = User.get(self.user_id)
        return {
            'user': {
                'id': user.id,
                'name': user.user_name,
                'avatar': user.avatar_url,
            },
            'name': self.name,
            'telephone': self.telephone,
            'id_card': self.id_card,
            'id_card_front': init_pic_url(self.id_card_front),
            'id_card_back': init_pic_url(self.id_card_back),
            'status': self.status,
            'reason': self.reason,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
        }


