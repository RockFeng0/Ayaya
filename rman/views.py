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

import logging

from flask import redirect
from rman import app


# 获取日志操作句柄
logger = logging.getLogger(__name__)

@app.route("/")
def index():
    return redirect('http://127.0.0.1:8080/login')

@app.after_request
def after_request(response):
    return response
