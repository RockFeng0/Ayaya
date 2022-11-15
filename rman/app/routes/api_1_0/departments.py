#! python3
# -*- encoding: utf-8 -*-


from flask import Blueprint
from flask_restful import Api
from rman.app.resources import department


departments = Blueprint('departments', __name__)

api = Api(departments)

api.add_resource(department.DepartmentListView, '')
api.add_resource(department.DepartmentView, '/<int:uid>')



