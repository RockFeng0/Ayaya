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

from flask import Blueprint
from flask_restful import Api
from rman.app.resources.tasks import TasksView

tasks = Blueprint('tasks', __name__)

api = Api(tasks)
api.add_resource(TasksView, '/list')

@tasks.route('/configs')
def get_tasks_cfgs():
    # GET /tasks/configs?task_id=32342
    return 'get tasks configs'


@tasks.route('/run', methods=['GET'])
def run_tasks():
    # GET /tasks/run?task_ids=1,2,3,4,5
    return 'run tasks'


@tasks.route('/status')
def get_tasks_status():
    # GET /tasks/status?task_ids=1,2,3,4,5
    return 'get tasks status'


@tasks.route('/report', methods=["GET"])
def get_tasks_report():
    # GET /tasks/report?task_id=32342
    return 'get tasks status'


@tasks.route('/caselogs/<log>')
def get_tasks_log(log):
    # GET /tasks/caselogs/xxx.log?task_id=32342
    return 'get tasks log'
