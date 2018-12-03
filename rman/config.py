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
#     SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # flask-wtf config
    SECRET_KEY = 'dsfsdfwe'
    
    ALL_BLUE_PRINT = {"auth":False, "httptest":True, "project":True}
    
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
