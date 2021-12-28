#! python3
# -*- encoding: utf-8 -*-
import re
import sys
import logging
import importlib

from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from rman import APP_ENV
from rman.app.common import log
from rman.app.config import configs

from werkzeug.contrib.cache import SimpleCache
simple_cache = SimpleCache()

# 获取日志对象
logger = logging.getLogger(__name__)
logger.addHandler(log.console)
logger.addHandler(log.log_handler)
logger.addHandler(log.err_handler)
logger.setLevel(logging.DEBUG)


def format_resp(body, code="200", message="success"):
    """
    响应的格式
    :param body:  本次请求的响应体
    :param code: 响应码， 默认值200，表示成功
    :param message: 响应码的描述， 默认值sucess
    """
    return {"code": code, "message": message, "body": body}


class FactoryCelery(Celery):
    def init_app(self, app):
        """
        flask 工厂模式，给celery实例对象，添加 应用上下文
        """
        self.conf.update(app.config)

        TaskBase = self.Task

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask
        return self

    def set_path(self):
        r""" use this to fix bugs if raise error:

        (test_pj) C:\d_disk\auto\git\rtsf-manager>celery -A rman.manager worker --loglevel info -c 1
        Traceback (most recent call last):
          File "<string>", line 1, in <module>
          File "c:\users\58-pc\virtualenvs\test_pj\lib\site-packages\billiard\forking.py", line 459, in main
            self = load(from_parent)
        ModuleNotFoundError: No module named 'rman'
        """
        if not '' in sys.path:
            sys.path.insert(0, "")

# 创建数据库对象： 处理数据库对象关系映射
db = SQLAlchemy()

# 创建跨域对象： 解决跨域问题
cors = CORS()

# 创建登录管理对象： 处理用户登录
login_manager = LoginManager()

# 创建加密对象： 处理用户登录密码
bcrypt = Bcrypt()

# 创建celery对象-： 处理异步任务
celery = FactoryCelery(__name__)


def create_app():
    """
    创建app
    """
    app = Flask(__name__)
    configuration = configs[APP_ENV]
    
    # 将配置读取到flask对象中
    app.config.from_object(configuration)

    # 对象的初始化
    configuration.init_app(app)
    db.init_app(app)    
    cors.init_app(app, supports_credentials=True)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    celery.init_app(app)

    # 处理蓝图
    blue_prints = app.config.get("ALL_BLUE_PRINT")
    for module_name, module_attr in blue_prints.items():
        # 开关是关闭的就跳过
        if module_attr.get("is_off"):
            continue

        m_name = module_name.split('.')[-1]
        # noinspection PyBroadException
        try:
            # 生成url前缀
            _end_point = "rman.app.routes.{0}".format(module_name)
            obj = importlib.import_module(_end_point)

            def __get_url_prefix():
                p = re.compile('(api)_([0-9]+)_([0-9]+)')
                f = lambda x: p.match(x)
                _end_point_list = _end_point.split('.')
                _url_prefix_list = _end_point_list[_end_point_list.index(list(filter(f, _end_point_list))[0]):] \
                    if list(filter(f, _end_point_list)) else []
                return p.sub('/\g<1>/v\g<2>.\g<3>', '/'.join(_url_prefix_list))

            # 注册蓝图并映射到endpoint, 默认使用自定义的蓝图，如果是不是自定义的蓝图，那么就会使用生成的蓝图
            url_pre = module_attr.get("url_prefix") if module_attr.get("url_prefix") else __get_url_prefix()
            app.register_blueprint(getattr(obj, m_name), url_prefix='{}'.format(url_pre))
        except Exception:
            logger.error(u'**** {0}\t module[{1}]'.format('fail', module_name), exc_info=True)
        else:
            logger.info(u'**** {0}\t module[{1}]'.format('pass', module_name))
    return app


# APP = create_app()
