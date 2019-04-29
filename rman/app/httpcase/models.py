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
    ''' http reqeusts case   '''

    __tablename__ = 't_rtsf_httpcase'
        
    id              = Column(Integer, primary_key=True)    
    name        = Column(String(32), comment = '用例名称')    
    
    suite_name      = Column(String(512), comment = '该case调用的suite名称')    
    api_name        = Column(String(512), comment = '该case调用的api名称')    
    
    func        = Column(String(512), comment = 'api的引用别名(def)')    
    #### manunal
    glob_var        = Column(String(512), comment = '全局变量（dict）')
    glob_regx       = Column(String(512), comment = '全局正则表达式（dict）')
    
    pre_command     = Column(String(512), comment = '测试用例前置条件(list)')
    url             = Column(String(512), nullable = False, comment = '请求url')
    method          = Column(String(4), nullable = False, comment = '请求方法(get or post)')
    headers        = Column(String(1024), comment = '请求头(dict)')
    body            = Column(String(1024), comment = '请求体(dict or str)')
    post_command    = Column(String(512), comment = '测试用例后置条件(list)')
    verify          = Column(String(512), comment = '验证条件(list)')
    test_set_id     = Column(Integer, nullable = False, comment = '隶属于case表-关联case表')
    
    create_time     = Column(DateTime, nullable = False)
    update_time     = Column(DateTime, nullable = False)

    def __init__(self, glob_var, glob_regx,pre_command,url,method,headers,body,post_command,verify,test_set_id,create_time,update_time):
        self.glob_var       = glob_var       
        self.glob_regx      = glob_regx
        self.pre_command    = pre_command
        self.url            = url
        self.method         = method
        self.headers       = headers
        self.body           = body
        self.post_command   = post_command
        self.verify         = verify
        self.test_set_id        = test_set_id 
        self.create_time    = create_time
        self.update_time    = update_time
          
    
    def __repr__(self):
        return '<HttpCase %r-%r>' % (self.url,self.id)
        

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
        self.exec_date      = exec_date
        self.exec_time      = exec_time
        self.duration       = duration
        self.total_cases    = total_cases
        self.pass_cases     = pass_cases
        self.fail_cases     = fail_cases
     
#     def has_testsets(self, testset_obj):
#         return self.testsets.filter(TestSet.proj_name == testset_obj.proj_name).count() > 0
#      
#     def append_testsets(self, testset_obj):
#         if not self.has_testsets(testset_obj):
#             self.testsets.append(testset_obj)
#             return self
#      
#     def remove_testsets(self, testset_obj):
#         if self.has_testsets(testset_obj):
#             self.testsets.remove(testset_obj)
#      
#     def get_testsets(self):
#         return TestSet.query.join(Run).filter(TestSet.run_id == self.id).all()
             
    def __repr__(self):
        return '<CaseRecord %r>' % (self.id)