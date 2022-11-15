#! python3
# -*- encoding: utf-8 -*-

import os


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
                        "api_0_0.auth":     {"is_off": True},
                        "api_0_0.manager":  {"is_off": True},
                        "api_0_0.httpcase": {"is_off": True, "url_prefix": "/httpcase"},
                        "api_0_0.rm_task":  {"is_off": True, "url_prefix": "/rm_task"},
                        "api_1_0.departments": {"is_off": False},
                        "api_1_0.projects": {"is_off": False},
                        "api_1_0.httpcases": {"is_off": False},
                        "views.tasks": {"is_off": False},
                        "views.user": {"is_off": False},
                        "views.auth": {"is_off": False},
                    }

    @staticmethod
    def init_app(app):
        pass


class ProdConfig(Config):
    # sqlalchemy mysql

    USERNAME = "xxx"
    PASSWORD = "xxx"
    HOST = "192.168.1.1"
    PORT = 3306
    DATABASE = 'xx_database'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8'.format(USERNAME, PASSWORD, HOST, PORT, DATABASE)


class DevConfig(Config):
    DEBUG = True
    # print(os.path.join(os.path.dirname(os.path.dirname(__file__)), "rman.db"))
    SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(os.path.dirname(os.path.dirname(__file__)), "rman.db"))


configs = {"production": ProdConfig, "testing": DevConfig}

