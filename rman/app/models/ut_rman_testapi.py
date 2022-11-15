#! python3
# -*- encoding: utf-8 -*-

from rman.app import db
from .base import BaseModel


class TestApiModel(db.Model, BaseModel):
    """
    预留单表: 组件用例
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'ut_rman_testapi'

    api_name = db.Column(db.String(32), nullable=False, comment='测试组件名称,即api_def,api别名')
    case_id = db.Column(db.Integer, comment="关联的httpcase id或者ui id，用于获取具体用例数据")

    test_type = db.Column(db.Integer, comment='标识改api的测试类型 1-httpcase, 2-ui')
    project_id = db.Column(db.Integer, nullable=False, comment='隶属项目的id')
