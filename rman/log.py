#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.log

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.log,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import os
import sys
import logging.handlers

logs_path = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(logs_path):
    os.mkdir(logs_path)

# 日志文件名称
server_log = os.path.join(os.path.dirname(__file__), "logs/server.log")
error_log = os.path.join(os.path.dirname(__file__), "logs/error.log")

# 定义handler
log_handler = logging.handlers.TimedRotatingFileHandler(
    server_log, when="D", backupCount=10, encoding="utf-8"
)
err_handler = logging.handlers.TimedRotatingFileHandler(
    error_log, when="D", backupCount=10, encoding="utf-8"
)
console = logging.StreamHandler(sys.stdout)

# 定义日志显示格式
fmt = "%(asctime)s - %(name)s - %(funcName)s - %(lineno)s -【%(levelname)s】- %(message)s"
formatter = logging.Formatter(fmt)

# 设置handler日志格式
log_handler.setFormatter(formatter)
err_handler.setFormatter(formatter)
console.setFormatter(formatter)

# 设置handler日志级别
log_handler.setLevel(logging.DEBUG)
err_handler.setLevel(logging.ERROR)
console.setLevel(logging.DEBUG)
