#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.views,  v1.0 2018年11月23日
    FROM:   2018年11月23日
********************************************************************
======================================================================

Provide a function for the automation test

'''
from flask import send_file
from rman.app import APP


@APP.route('/', methods = ["GET"])
def index():
    return send_file('index.html')
