import logging, importlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Separator

from rman.config import config
from rman.log import console,log_handler,err_handler

logger = logging.getLogger(__name__)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

cors = CORS()
db = SQLAlchemy()
bootstrap = Bootstrap()
nav=Nav()
def create_app(env=None):
    app = Flask(__name__)
    configuration = config[env] if env else config["testing"]
    
    if env == 'production':
        logger.addHandler(log_handler)
        logger.addHandler(err_handler)

    # 将配置读取到flask对象中
    app.config.from_object(configuration)
    configuration.init_app(app)
    cors.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    nav.register_element('top',Navbar(u'rtsf自动化用例管理',
                                View(u'主页','index'),
                                View(u'关于','about'),
                                Subgroup(u'项目管理',
                                         View(u'项目列表','project.search'),
                                         Separator(),
                                         View(u'调试-项目更新', 'project.update'),
                                         View(u'调试-删除项目', 'project.delete'),
                                         ),
                                )
                        )
    nav.init_app(app)
    
    # 依据config， 注册蓝图
    blue_prints = app.config.get("ALL_BLUE_PRINT")
    
    from rman.project import project
    app.register_blueprint(project, url_prefix = '/project')
    
#     for module_name,module_switch in blue_prints.items():
#         if module_switch:
#             try:
#                 obj = importlib.import_module("rman.{0}.{0}".format(module_name))
#                 app.register_blueprint(obj, url_prefix = '/{}'.format(module_name))
#             except Exception as e:
#                 logger.error('{0}启动【{1}】模块失败，跳过！{0}'.format('×' * 15, module_name))
#                 logger.exception(e)
#             else:
#                 logger.info('{0}【{1}】模块启动成功{0}'.format('√' * 15, module_name))

    return app

env = "testing"
app = create_app(env)

# 加载顶层视图函数，缺少下面的语句会导致views中的视图函数注册失败
from .views import *



