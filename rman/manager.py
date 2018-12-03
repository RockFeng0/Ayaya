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
from rman import app, db
from flask_migrate import Migrate

from rman.auth.models import User
from rman.httptest.models import Case, CaseItemRequest
from rman.project.models import Project

migrate = Migrate(app,db)


