#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.rm_task.models

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.rm_task.models,  v1.0 2019年12月5日
    FROM:   2019年12月5日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman.app import db
from sqlalchemy import Column, Integer, String,  DateTime

class Rmtask(db.Model):
    ''' 测试项目  '''
    __tablename__ = 't_rtsf_task'
        
    id           = Column(Integer, primary_key=True)
    case         = Column(String(64), nullable = False, comment = u'测试集名称')    
    desc         = Column(String(64), nullable = True, comment = u'任务描述')
    tid          = Column(String(128), nullable = True, comment = u'任务ID')
    status       = Column(Integer, nullable = True, default=0,  comment = u'0-未执行, 1-执行中, 2-执行成功, 3-执行失败, 4-无效脚本， 5-redis服务异常')
    report_url   = Column(String(128), nullable = True, comment = u'报告链接')
    report_path  = Column(String(128), nullable = True, comment = u'报告路径')
    
           
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):        
        _ = [setattr(self, k, v) for k,v in kwargs.items()]    
           
    def __repr__(self):
        return '<Rmtask %r>' % (self.id)
