#! python3
# -*- encoding: utf-8 -*-


from rman.app import db
from .base import BaseModel


class ModuleModel(db.Model, BaseModel):
    """
    测试模块表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'm_module'

    name = db.Column(db.String(64), unique=True, nullable=False, comment=u'模块名称')
    project_id = db.Column(db.Integer, nullable=False, default=0, comment=u'项目id')

