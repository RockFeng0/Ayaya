#! python3
# -*- encoding: utf-8 -*-
"""
Rough version history:
v1.0    Original version to use
********************************************************************
    @AUTHOR:  罗科峰
    MAIL:     luokefengds@chinamobile.com
    RCS:      tasks.py,  v1.0 2020/9/4
    FROM:     2020/9/4
********************************************************************

"""

from flask_restful import Resource


DATAS = {
    'test': "hello tasks",
}


class TasksView(Resource):
    def get(self):
        return DATAS["test"]

