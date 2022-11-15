#! python3
# -*- encoding: utf-8 -*-


from flask import Blueprint
from flask_restful import Api
from rman.app.resources import project


projects = Blueprint('projects', __name__)

api = Api(projects)

api.add_resource(project.ProjectListView, '')
api.add_resource(project.ProjectView, '/<int:uid>')



