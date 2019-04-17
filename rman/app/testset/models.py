#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.case.models

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.case.models,  v1.0 2019年4月12日
    FROM:   2019年4月12日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman.app import db
from sqlalchemy import Column, Integer, String, DateTime
    
class TestSet(db.Model):
    ''' 测试集     关系    TestSet--1:M--Case* '''
    __tablename__ = 't_rtsf_testset'
        
    id              = Column(Integer, primary_key=True)    
    name            = Column(String(32), nullable = False, comment = '测试集名称，简要描述用途')
    desc            = Column(String(64), comment = '测试集， 详细描述')
    responsible     = Column(String(32), comment = '测试集，责任人或编写人员')
    tester          = Column(String(32), comment = '测试集，执行人或运行的人')
    type            = Column(String(10), nullable = False, default = "case", comment = '测试集的类型，值: api、suite、case')
    suite_def       = Column(String(64), nullable = True, comment = '测试套件的引用名，如果type是suite是，该字段必填')    
        
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, name,desc,responsible,tester,tp, suite_def, create_time,update_time):
        self.name        = name        
        self.desc        = desc       
        self.responsible = responsible
        self.tester      = tester
        self.type        = tp     
        self.suite_def   = suite_def      
                
        self.create_time = create_time
        self.update_time = update_time    
    
    def __repr__(self):
        return '<TestSet %r-%r>' % (self.name,self.id)
