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

from . import app
# from flask_wtf.csrf import generate_csrf

# 获取日志操作句柄
logger = logging.getLogger(__name__)


@app.after_request
def after_request(response):
    # CSRF问题
#     response.set_cookie("token", generate_csrf())
    return response
