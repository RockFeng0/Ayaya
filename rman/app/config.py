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
import sys, os

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
    
    #### Celery 
    CELERY_TIMEZONE='Asia/Shanghai'
    # CELERY_TIMEZONE='UTC'                             
        
    CELERY_IMPORTS = (
        "rman.tasks.run_case.r_http",
    )
    
    
    # 蓝图开关
    ALL_BLUE_PRINT = {
                        "auth":False,
                        "runner": False,
                        "manager":True,
                        "httpcase":True,
                        "rm_task":True,                         
                    }
    
    @staticmethod
    def init_app(app):
        pass
    
class ProdConfig(Config):    
    # sqlalchemy mysql
    
    USERNAME = "xxx"
    PASSWORD = "xxx"
    HOST = "localhost"
    PORT = 3306
    DATABASE = 'dbcs_qa_biz_rman'    
     
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(USERNAME,PASSWORD,HOST,PORT,DATABASE)
    
    #### Celery
    BROKER_URL = 'redis://:58cstest@abc@127.0.0.1:6379'    
    CELERY_RESULT_BACKEND = 'redis://:58cstest@abc@localhost:6379'
    YAML_CASE_PATH = "/opt/deploy/rock4tools/rtsf-cases/rman-gen"
    
class DevConfig(Config):
    DEBUG=True
    #print(os.path.join(os.path.dirname(os.path.dirname(__file__)), "rman.db"))
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(os.path.dirname(os.path.dirname(__file__)), "rman.db"))
    
    #### Celery
    BROKER_URL = 'redis://:123456@127.0.0.1:6379'
    CELERY_RESULT_BACKEND = 'redis://:123456@127.0.0.1:6379/0'
#     YAML_CASE_PATH = r"C:\d_disk\auto\buffer\test\rtsf-cases\rman-gen"
    YAML_CASE_PATH = r"C:\d_disk\auto\git\rtsf-manager\rman\logs"

configs = {"production":ProdConfig, "testing":DevConfig}
