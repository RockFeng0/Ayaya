import logging, importlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from rman.config import config
from rman.log import console,log_handler,err_handler

from werkzeug.contrib.cache import SimpleCache
simple_cache = SimpleCache()

logger = logging.getLogger(__name__)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

db = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(env=None):
    app = Flask(__name__)
    configuration = config[env] if env else config["testing"]
    
    if env == 'production':
        logger.addHandler(log_handler)
        logger.addHandler(err_handler)

    # 将配置读取到flask对象中
    app.config.from_object(configuration)
    configuration.init_app(app)
    db.init_app(app)    
    cors.init_app(app, supports_credentials=True)
    login_manager.init_app(app)
    bcrypt.init_app(app)
        
    blue_prints = app.config.get("ALL_BLUE_PRINT")
    for module_name,module_switch in blue_prints.items():        
        if module_switch:
            try:
                obj = importlib.import_module("rman.{0}".format(module_name))
                app.register_blueprint(getattr(obj,module_name), url_prefix = '/{}'.format(module_name))
            except Exception as e:
                logger.error('启动【{1}】模块失败，跳过！\t{0}'.format('×', module_name))
                logger.exception(e)
            else:
                logger.info('启动【{1}】模块成功.\t{0}'.format('√', module_name))

    return app


env = "testing"
app = create_app(env)


# 加载顶层视图函数，缺少下面的语句会导致views中的视图函数注册失败
from .views import *



