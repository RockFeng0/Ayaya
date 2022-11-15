#! python3
# -*- encoding: utf-8 -*-


from rman.app import db
from rman.app.models.base import BaseModel


class TaskRecordModel(db.Model, BaseModel):
    """
    测试执行的任务流水表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'task_record'

    case = db.Column(db.String(64), nullable=False, comment=u'测试集名称')
    desc = db.Column(db.String(64), nullable=True, comment=u'任务描述')
    tid = db.Column(db.String(128), nullable=True, default="", comment=u'任务ID')
    status = db.Column(db.Integer, nullable=True, default=0, comment=u'0-未执行, 1-执行中, 2-执行成功, 3-执行失败, '
                                                                     u'4-无效脚本， 5-redis服务异常, 6-取消执行')
    report_url = db.Column(db.String(128), nullable=True, default="", comment=u'报告链接')
    report_path = db.Column(db.String(128), nullable=True, default="", comment=u'报告路径')


STATUS_MAP = {
    0: "未执行",
    1: "执行中",
    2: "执行成功",
    3: "执行失败",
    4: "无效脚本",
    5: "redis服务异常",
    6: "取消执行",
}
