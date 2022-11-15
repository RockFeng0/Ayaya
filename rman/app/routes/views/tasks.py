#! python3
# -*- encoding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api
from rman.app.resources.tasks import record, conf

tasks = Blueprint('tasks', __name__)

api = Api(tasks)
api.add_resource(record.TaskListView, '/task/record')
api.add_resource(record.TaskView, '/task/record/<int:sid>')
api.add_resource(conf.TaskConfigListView, '/task')
api.add_resource(conf.TaskConfigView, '/task/<int:sid>')
