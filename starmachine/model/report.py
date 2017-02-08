# coding: utf-8

from datetime import datetime
from starmachine.lib.query import DbManager
from starmachine.model.consts import CHECK_STATUS_PENDING, CHECK_STATUS_PASS, CHECK_STATUS_REJECT


class Report(object):

    table = 'report'

    def __init__(self, id=None, reporter_id=None, report_type=None, report_dist=None, status=None, reason=None,
        create_time=None, check_time=None, extra=None):
        self.id = id
        self.reporter_id = reporter_id
        self.report_type = report_type
        self.report_dist = report_dist
        self.status = status
        self.reason = reason
        self.create_time = create_time
        self.check_time = check_time
        self.extra = extra

    @classmethod
    def add(cls, reporter_id, report_type, report_dist, reason, status=CHECK_STATUS_PENDING):
        create_time = datetime.now()
        db = DbManager().db
        sql = 'insert into {table} (reporter_id, report_type, report_dist, reason, status, create_time) values ' \
            '(%s, %s, %s, %s, %s, %s)'.format(table=cls.table)
        db.execute(sql, reporter_id, report_type, report_dist, reason, status, create_time)

    def pass_report(self, extra):
        db = DbManager().db
        check_time = datetime.now()
        sql = 'update {table} set status=%s, check_time=%s, extra=%s where id=%s'.format(table=self.table)
        db.execute(sql, CHECK_STATUS_PASS, extra, check_time, self.id)

    def reject_report(self, extra):
        db = DbManager().db
        check_time = datetime.now()
        sql = 'update {table} set status=%s, check_time=%s, extra=%s where id=%s'.format(table=self.table)
        db.execute(sql, CHECK_STATUS_REJECT, extra, check_time, self.id)