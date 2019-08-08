#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.httptest.models

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.httptest.models,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman.app import db
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, Date, Time
    
class HttpCase(db.Model):
    ''' http reqeusts case '''

    __tablename__ = 't_rtsf_httpcase'
        
    id          = Column(Integer, primary_key=True)    
    
    glob_var    = Column(String(512), comment = '全局变量（dict）')
    glob_regx   = Column(String(512), comment = '全局正则表达式（dict）')
    
    pre_command  = Column(String(512), comment = '测试用例前置条件(list)')
    url          = Column(String(512), nullable = False, comment = '请求url')
    method       = Column(String(4), nullable = False, comment = '请求方法(get or post)')
    headers      = Column(String(1024), comment = '请求头(dict)')
    body         = Column(String(1024), comment = '请求体dict')
    files        = Column(String(1024), comment = '上传的文件dict')
    post_command = Column(String(512), comment = '测试用例后置条件(list)')
    verify       = Column(String(512), comment = '验证条件(list)')
        
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]    
           
    def __repr__(self):
        return '<HttpCase %r>' % (self.id)
        

class CaseRecord(db.Model):
    ''' Record the running cases '''
    __tablename__ = 't_rtsf_case_record'
     
    id          = Column(Integer, primary_key=True)
    exec_date   = Column(Date)
    exec_time   = Column(Time)
    duration    = Column(Integer)
    total_cases = Column(Integer)
    pass_cases  = Column(Integer)
    fail_cases  = Column(Integer)
     
    def __init__(self, exec_date, exec_time, duration, total_cases, pass_cases, fail_cases):        
        pass
             
    def __repr__(self):
        return '<CaseRecord %r>' % (self.id)

from rman.app.manager.models import ManagerQuerys, TestCases, TestApis, TestSuites, TestSuiteApiRelation

class HttpCaseQuerys(ManagerQuerys):    
    
    @staticmethod
    def t_hcase():
        return db.session.query(HttpCase)
    
    @staticmethod
    def j_tcase_hcase():
        return db.session.query(TestCases, HttpCase).outerjoin(HttpCase, TestCases.call_manunal_id == HttpCase.id)
    
    @staticmethod
    def j_api_hcase():
        return db.session.query(TestApis, HttpCase).join(HttpCase, TestApis.call_manunal_id == HttpCase.id)
    
    @staticmethod
    def j_suite_relation_api():
        return db.session.query(TestSuiteApiRelation.name, TestApis.api_def).join(TestApis, TestSuiteApiRelation.api_id == TestApis.id)                
                
        