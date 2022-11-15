#! python3
# -*- encoding: utf-8 -*-


from rman.app import db
from .base import BaseModel


class DepartmentModel(db.Model, BaseModel):
    """
    部门表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'm_department'

    name = db.Column(db.String(64), unique=True, nullable=False, comment=u'部门名称')
