#! python3
# -*- encoding: utf-8 -*-


from rman.app import db
from .base import BaseModel


class TestCaseModel(db.Model, BaseModel):
    """
    测试用例表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'test_case'

    name = db.Column(db.String(32), nullable=False, comment='测试用例名称')
    desc = db.Column(db.String(64), comment='详细描述')
    responsible = db.Column(db.String(32), default="Administrator", comment='责任人或编写人员')
    tester = db.Column(db.String(32), default="Administrator", comment='执行人或运行的人')
    module_id = db.Column(db.Integer, nullable=False, comment="隶属模块的id")
