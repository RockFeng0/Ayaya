#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.auth.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.auth.views,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from . import auth
from .models import User
from rman import login_manager

_query = User.query

@login_manager.user_loader
def load_user(userid):
    return _query.filter_by(id = userid).first()

@auth.route("/login", methods = ["POST"])
def login():
    pass
