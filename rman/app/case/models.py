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
    
class Case(db.Model):
    ''' 测试用例   -> 所有的测试用例    '''
    __tablename__ = 'case'
        
    id              = Column(Integer, primary_key=True)    
    name            = Column(String(32), nullable = False, comment = '测试用例名称')
    desc            = Column(String(64), comment = '用例的简单描述')    
    responsible     = Column(String(32), comment = '测试责任人或者用例编写人员')
    tester          = Column(String(32), comment = '测试执行人或者运行该用例的人员')
    case_type       = Column(String(10), nullable = False, default = "case", comment = '0-api, 1-case, 2-suite')
    func            = Column(String(64), nullable = True, comment = 'api或者suite的函数名称(必填)， case无要求')    
        
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, name,desc,responsible,tester,case_type, func, create_time,update_time):
        self.name        = name        
        self.desc        = desc       
        self.responsible = responsible
        self.tester      = tester
        self.case_type   = case_type     
        self.func        = func      
                
        self.create_time = create_time
        self.update_time = update_time    
    
    def __repr__(self):
        return '<Case %r-%r>' % (self.name,self.id)
