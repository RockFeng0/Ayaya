#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.config

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.config,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''

class Config(object):
    # 防止返回的json中汉字被转码
    JSON_AS_ASCII = False
    SECRET_KEY = 'lskdjflsj'
    TOKEN_LIFETIME = 3600 
    
    # flask-sqlalchemy 数据库 - 请求执行完逻辑之后自动提交，而不用我们每次都手动调用session.commit(); 我还是习惯，自己 commit
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    
    # flask-sqlalchemy 数据库 - 需要设定参数True 或者 Flase,是说SQLALCHEMY_TRACK_MODIFICATIONS不能默认什么都没有
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # flask-login
    REMEMBER_COOKIE_NAME = "token"
    
    # 蓝图开关
    ALL_BLUE_PRINT = {"auth":True, "httptest":False, "project":True}
    
    @staticmethod
    def init_app(app):
        pass
    
class ProdConfig(Config):
    host = "localhost"
    port = 3306
    user = "xxx"
    passwd = "xxx"
    name = 'rman'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user,passwd,host,user,name)    
 
class DevConfig(Config):
    DEBUG=True    
    SQLALCHEMY_DATABASE_URI = "sqlite:///rman.db"

config = {"production":ProdConfig, "testing":DevConfig}
