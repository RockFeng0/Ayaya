#! python3
# -*- encoding: utf-8 -*-


from rman.app import db
from .base import BaseModel


class ProjectModel(db.Model, BaseModel):
    """
    测试项目表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'm_project'

    name = db.Column(db.String(64), unique=True, nullable=False, comment=u'项目名称')
    comment = db.Column(db.String(128), nullable=True, comment=u'备注')
    department_id = db.Column(db.Integer, nullable=False, default=0, comment=u'所属部门id')
