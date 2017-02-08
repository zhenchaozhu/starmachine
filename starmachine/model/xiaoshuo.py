# coding: utf-8

from starmachine.lib.query import DbManager

class XiaoShuo(object):

    table = 'xiaoshuo'

    def __init__(self, id, link_uri, img_uri, article_title, article_desc):
        self.id = id
        self.link_uri = link_uri
        self.img_uri = img_uri
        self.article_title = article_title
        self.article_desc = article_desc

    @classmethod
    def gets_all(cls):
        db = DbManager().db
        sql = 'select * from {table}'.format(table=cls.table)
        rst = db.query(sql)
        return rst and [cls(**d) for d in rst]


class XiaoShuoFocusPic(object):

    table = 'xiaoshuo_focuspic'

    def __init__(self, id, link_uri, img_uri, focus_desc):
        self.id = id
        self.link_uri = link_uri
        self.img_uri = img_uri
        self.focus_desc = focus_desc

    @classmethod
    def get_focus_pic(cls):
        db = DbManager().db
        sql = 'select * from {table} limit 1'.format(table=cls.table)
        rst = db.get(sql)
        return rst and cls(**rst)
