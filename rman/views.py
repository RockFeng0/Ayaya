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
from flask import render_template


# 获取日志操作句柄
logger = logging.getLogger(__name__)


    
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.after_request
def after_request(response):
    # 跨域问题
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
#     response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = '*'    
#     response.headers['Access-Control-Expose-Headers'] = '*'  
    return response
