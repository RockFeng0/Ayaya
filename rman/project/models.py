#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.project.models

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.project.models,  v1.0 2018年11月30日
    FROM:   2018年11月30日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman import db
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime

class Project(db.Model):
    ''' 测试项目  '''
    __tablename__ = 'project'
        
    id              = Column(Integer, primary_key=True)
    name            = Column(String(64), nullable = False, comment = '项目名称')
    module          = Column(String(64), nullable = False, comment = '项目功能模块')
    comment         = Column(String(128), nullable = True, comment = '备注')
           
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, name, module, comment,create_time,update_time):  
        self.name        = name 
        self.module      = module       
        self.comment     = comment
        self.create_time = create_time
        self.update_time = update_time    
    
    def __repr__(self):
        return '<Project %r-%r>' % (self.name,self.id)
    

