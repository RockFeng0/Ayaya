#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.tasks.celeryconfig

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.tasks.celeryconfig,  v1.0 2019年8月3日
    FROM:   2019年8月3日
********************************************************************
======================================================================

Provide a function for the automation test

'''

class Config(object):    
    
    CELERY_TIMEZONE='Asia/Shanghai'
    # CELERY_TIMEZONE='UTC'                             
        
    CELERY_IMPORTS = (
        "rman.tasks.run_case.r_http",
    )
    

class DevConfig(Config):
    
    BROKER_URL = 'redis://:123456@127.0.0.1:6379'
    CELERY_RESULT_BACKEND = 'redis://:123456@127.0.0.1:6379/0'
#     YAML_CASE_PATH = r"C:\d_disk\auto\buffer\test\rtsf-cases\rman-gen"
    YAML_CASE_PATH = r"C:\d_disk\auto\buffer\test\rtsf-cases\rtsf-http-test"
    
class ProdConfig(Config):
    BROKER_URL = 'redis://:58cstest@abc@127.0.0.1:6379'    
    CELERY_RESULT_BACKEND = 'redis://:58cstest@abc@localhost:6379'
    YAML_CASE_PATH = "/opt/deploy/rock4tools/rtsf-cases/rman-gen"


configs = {"production":ProdConfig, "testing":DevConfig}
