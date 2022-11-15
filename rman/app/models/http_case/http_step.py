#! python3
# -*- encoding: utf-8 -*-

from rman.app import db
from rman.app.models.base import BaseModel


class HttpStepModel(db.Model, BaseModel):
    """
    HTTP接口入参表 -http测试用例
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'http_step'

    name = db.Column(db.String(32), nullable=False, comment='测试步骤或用例名称')

    glob_var = db.Column(db.String(512), comment='全局变量（dict）')
    glob_regx = db.Column(db.String(512), comment='全局正则表达式（dict）')

    pre_command = db.Column(db.String(1024), comment='测试用例前置条件(list)')
    url = db.Column(db.String(512), nullable=False, comment='请求url')
    method = db.Column(db.Integer, nullable=False, comment='请求方式 0-post,1-get,2-put,3-delete')
    headers = db.Column(db.String(1024), comment='请求头(dict)')
    body = db.Column(db.String(5000), comment='请求体dict')
    files = db.Column(db.String(1024), comment='上传的文件dict')
    post_command = db.Column(db.String(512), comment='测试用例后置条件(list)')
    verify = db.Column(db.String(512), comment='验证条件(list)')

    step_type = db.Column(db.Integer, nullable=True, default=1001, comment=u'步骤或用例类型')
    case_args = db.Column(db.String(1024), comment='预留字段: 调用组件或套件用例时传参')

    api_id = db.Column(db.Integer, nullable=True, comment="隶属HttpApi的id")
    testcase_id = db.Column(db.Integer, nullable=False, comment="隶属TestCase的id")


CASE_TYPE_MAP = {
    1001: "原始用例",
    1002: "组件用例",
}

METHOD_TYPE_MAP = {
    "POST": 0,
    "GET": 1,
    "PUT": 2,
    "DELETE": 3
}
