#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.manager

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.manager,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''
from rman.app import create_app, celery, db
from flask_migrate import Migrate

APP = create_app()

migrate = Migrate(APP, db)
celery.set_path()


if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=5000, debug=True)