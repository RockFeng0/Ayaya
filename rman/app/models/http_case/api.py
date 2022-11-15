#! python3
# -*- encoding: utf-8 -*-

from rman.app import db
from rman.app.models.base import BaseModel


class HttpApiModel(db.Model, BaseModel):
    """
    HTTP接口配置表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'http_api'

    name = db.Column(db.String(100), nullable=False, unique=True, comment=u'接口名称')
    url = db.Column(db.String(100), nullable=False, comment=u'请求地址')
    method = db.Column(db.Integer, nullable=False, default=0, comment='请求方法')
    params = db.Column(db.String(100), nullable=True, default='', comment=u'请求参数')
    headers = db.Column(db.String(100), nullable=True, default='', comment=u'请求头部')
    updater = db.Column(db.String(128), nullable=True, default='', comment=u'更新人')
    module_id = db.Column(db.Integer, nullable=True, comment=u'隶属的项目模块id')


METHOD_MAP = {
    1: "GET",
    2: "POST",
    3: "PUT",
    4: "DELETE"
}
