#! python3
# -*- encoding: utf-8 -*-


from rman.app import db
from .base import BaseModel


class TestSuiteModel(db.Model, BaseModel):
    """
    预留单表: 套件用例
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'ut_rman_testsuite'

    suite_name = db.Column(db.String(32), nullable=False, comment='测试套件名称,作为suite_def')
    project_id = db.Column(db.Integer, nullable=False, comment='隶属项目的id')
