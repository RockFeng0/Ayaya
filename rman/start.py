#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.start

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.start,  v1.0 2019年4月4日
    FROM:   2019年4月4日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import sys
from rman import APP_ENV 
from rman.app import APP

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


if __name__ == "__main__":
    if APP_ENV == "testing":
        APP.run(host='0.0.0.0', port=5000, debug = True)
    else:
        #  注意 vue.js中，ip和端口的切换
        sys.path.append('/opt/deploy/rock4tools/rman')
        http_server = HTTPServer(WSGIContainer(APP))
        http_server.listen(5001)
        IOLoop.instance().start()
        