#! python3
# -*- encoding: utf-8 -*-

import logging, importlib, sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from rman import APP_ENV, log
from rman.app.config import configs
from rman.tasks import FactoryCelery


from werkzeug.contrib.cache import SimpleCache
simple_cache = SimpleCache()

logger = logging.getLogger(__name__)
logger.addHandler(log.console)
logger.addHandler(log.log_handler)
logger.addHandler(log.err_handler)
logger.setLevel(logging.DEBUG)


db = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()
bcrypt = Bcrypt()
celery = FactoryCelery(__name__)

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def create_app():
    app = Flask(__name__)
    configuration = configs[APP_ENV]
    
    # 将配置读取到flask对象中
    app.config.from_object(configuration)
    configuration.init_app(app)
    db.init_app(app)    
    cors.init_app(app, supports_credentials=True)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    celery.init_app(app)
        
    blue_prints = app.config.get("ALL_BLUE_PRINT")
    for module_name,module_switch in blue_prints.items():        
        if module_switch:
            try:
                obj = importlib.import_module("rman.app.{0}".format(module_name))
                m_name = module_name.split('.')[-1]
                app.register_blueprint(getattr(obj,m_name), url_prefix = '/{}'.format(m_name))
            except Exception:
                logger.error(u'**** {0}\t module[{1}]'.format('fail', m_name), exc_info = True)
            else:
                logger.info(u'**** {0}\t module[{1}]'.format('pass', m_name))

    return app






