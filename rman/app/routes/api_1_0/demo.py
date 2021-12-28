#! python3
# -*- encoding: utf-8 -*-
"""
Rough version history:
v1.0    Original version to use
********************************************************************
    @AUTHOR:  罗科峰
    MAIL:     luokefengds@chinamobile.com
    RCS:      demo.py,  v1.0 2020/9/4
    FROM:     2020/9/4
********************************************************************

"""

from flask import Blueprint
from flask_restful import Api
from rman.app.resources.demo.case import Case
from rman.app.resources.demo.user import TodoList, Todo

demo = Blueprint('demo', __name__)

api = Api(demo)
api.add_resource(Case, '/case/<case_id>')
api.add_resource(TodoList, '/user/todos')
api.add_resource(Todo, '/user/todos/<todo_id>')

@demo.route('/list')
def get_tasks_log():
    return 'get demo list'