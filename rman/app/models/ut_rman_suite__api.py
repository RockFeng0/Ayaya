#! python3
# -*- encoding: utf-8 -*-

from rman.app import db
from .base import BaseModel


class SuiteApiRelationModel(db.Model, BaseModel):
    """
    Suite与Api 多对多关系表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'm_suite__api'

    api_id = db.Column(db.Integer, nullable=False, comment='组件ID')
    suite_id = db.Column(db.Integer, nullable=False, comment='套件ID')
