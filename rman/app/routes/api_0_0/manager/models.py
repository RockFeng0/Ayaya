#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.manager.models

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.manager.models,  v1.0 2019年5月30日
    FROM:   2019年5月30日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman.app import db
from sqlalchemy import Column, Integer, String, DateTime
    
    
class TestProject(db.Model):
    ''' 测试项目     关系      Project-- M:M -- TestSet '''
    __tablename__ = 't_rtsf_test_project'
        
    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String(64), comment = '项目名称')
    module          = Column(String(64), comment = '项目功能模块')
    comment         = Column(String(128), nullable = True, comment = '备注')
           
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]
        
    def __repr__(self):
        return '<TestSet %r>' %(self.id)

class TestSet(db.Model):
    ''' 测试集     关系    TestSet--1:M--Case* '''
    __tablename__ = 't_rtsf_test_set'
        
    id              = Column(Integer, primary_key=True)    
    name            = Column(String(32), comment = '测试集名称')
    desc            = Column(String(64), comment = '详细描述')
    responsible     = Column(String(32), comment = '责任人或编写人员')
    tester          = Column(String(32), comment = '执行人或运行的人')
    
    project_id      = Column(Integer, nullable = False, comment = '隶属项目的id')  
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]
        
    def __repr__(self):
        return '<TestSet %r>' %(self.id)
    
class TestSuites(db.Model):
    ''' 测试项目  '''
    __tablename__ = 't_rtsf_test_suite'
        
    id              = Column(Integer, primary_key=True)
    suite_def       = Column(String(64), nullable = False, comment = '套件别名')    
    
    project_id      = Column(Integer, nullable = False, comment = '隶属项目的id')    
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]
        
    def __repr__(self):
        return '<TestSuites %r>' %(self.id)
    
class TestApis(db.Model):
    ''' 测试项目  '''
    __tablename__ = 't_rtsf_test_api'
        
    id              = Column(Integer, primary_key=True)
    api_def         = Column(Integer, nullable = False, comment = 'api别名')
    call_manunal_id = Column(Integer, nullable = False, comment = '调用的用例id')
    
    project_id      = Column(Integer, nullable = False, comment = '隶属项目的id')    
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]
        
    def __repr__(self):
        return '<TestApis %r>' %(self.id)
    
class TestSuiteApiRelation(db.Model):
    ''' 测试项目  '''
    __tablename__ = 't_rtsf_test_api_suite_relation'
        
    id              = Column(Integer, primary_key=True)
    suite_id        = Column(Integer, nullable = False, comment = '套件 id')
    api_id          = Column(Integer, nullable = False, comment = 'API id')
    name            = Column(Integer, nullable = False, comment = '用例名称')
    
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]
        
    def __repr__(self):
        return '<TestSuiteApiRelation %r>' %(self.id)
    
class TestCases(db.Model):
    ''' 测试项目  '''
    __tablename__ = 't_rtsf_test_case'
        
    id              = Column(Integer, primary_key=True)
    name            = Column(Integer, nullable = False, comment = '用例名称')
    
    # 下面三个，仅填写一个
    call_suite      = Column(String(32), comment = '该case调用的suite def-带参数')    
    call_api        = Column(String(32), comment = '该case调用的api def-带参数')
    call_manunal_id = Column(Integer, comment="该case调用的manunal_id")
    
    test_set_id     = Column(Integer, nullable=False, comment="隶属测试集的id")    
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, **kwargs):
        _ = [setattr(self, k, v) for k,v in kwargs.items()]    
        
    def __repr__(self):
        return '<TestCases %r>' %(self.id)
    
class ManagerQuerys(object):
    
    @staticmethod
    def t_project():
        return db.session.query(TestProject)
        
    @staticmethod
    def t_set():
        return db.session.query(TestSet)
       
    @staticmethod
    def t_suite():
        return db.session.query(TestSuites)
    
    @staticmethod
    def t_suite_api_relation():
        return db.session.query(TestSuiteApiRelation)
        
    @staticmethod
    def t_api():
        return db.session.query(TestApis)
    
    @staticmethod
    def t_case():
        return db.session.query(TestCases)
    
    @staticmethod
    def j_project_set():
#         return db.session.query(TestSet, TestProject).join(TestProject,TestSet.project_id == TestProject.id)
        return db.session.query(TestProject, TestSet).join(TestSet, TestSet.project_id == TestProject.id)
        