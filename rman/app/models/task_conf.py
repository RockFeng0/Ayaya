#! python3
# -*- encoding: utf-8 -*-

import datetime
from rman.app import db
from rman.app.models.base import BaseModel


class TaskConfigModel(db.Model, BaseModel):
    """
    测试任务配置表
    """
    # __bind_key__ = 'auto'
    __tablename__ = 'task_conf'

    task_name = db.Column(db.String(200), unique=True, nullable=False, comment=u'任务名称')
    cases = db.Column(db.String(200), nullable=True, comment=u'待执行的用例')
    task_ids = db.Column(db.String(200), nullable=True, comment=u'任务ids列表')
    is_timed_task = db.Column(db.Boolean, default=False, nullable=False, comment=u'是否是定时任务')
    task_plan = db.Column(db.DATETIME, default=datetime.datetime.now, comment=u'任务计划')
    is_active = db.Column(db.Boolean, default=False, nullable=True, comment=u'是否激活')
    is_run = db.Column(db.Boolean, default=False, nullable=True, comment=u'是否执行')
    update_person = db.Column(db.String(32), nullable=True, comment=u'更新人')
    run_time = db.Column(db.DATETIME(6), nullable=True, comment=u'执行时间')
    active_time = db.Column(db.DATETIME(6), nullable=True, comment=u'激活时间')
    department_id = db.Column(db.Integer, nullable=False, default=0, comment=u'所属部门id')
