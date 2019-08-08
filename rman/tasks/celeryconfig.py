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

from celery.schedules import crontab

class Config(object):    
    
    CELERY_TIMEZONE='Asia/Shanghai'
    # CELERY_TIMEZONE='UTC'                             
        
    CELERY_IMPORTS = (
        'bztest.tasks.task1',
        'bztest.tasks.check_daily',
        'bztest.tasks.check_birthday',
        "bztest.tasks.http_test",
    )
    
    # schedules
#     CELERYBEAT_SCHEDULE = {
#         'schedule_daily_check': {
#             'task': 'bztest.tasks.check_daily.run_daily_check',
#             'schedule': crontab(hour=16, minute=25),
#             'kwargs': {"debug":True}
#         },
#         'schedule_birthday_check': {
#             'task': 'bztest.tasks.check_birthday.run_birthday_check',
#             'schedule': crontab(hour=10, minute=10),
#             'kwargs': {"is_check_today":True, "debug":True}
#         }
#     }

class DevConfig(Config):
    
    BROKER_URL = 'redis://:123456@127.0.0.1:6379'
    CELERY_RESULT_BACKEND = 'redis://:123456@127.0.0.1:6379/0'
    
class ProdConfig(Config):
    BROKER_URL = 'redis://:58cstest@abc@127.0.0.1:6379'    
    CELERY_RESULT_BACKEND = 'redis://:58cstest@abc@localhost:6379'


configs = {"production":ProdConfig, "testing":DevConfig}
