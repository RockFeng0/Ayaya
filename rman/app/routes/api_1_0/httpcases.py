#! python3
# -*- encoding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api
from rman.app.resources.httpcases import api as httpapi
from rman.app.resources.httpcases import testcase

httpcases = Blueprint('httpcases', __name__)

api = Api(httpcases)
api.add_resource(testcase.HttpCaseListView, '/case')
api.add_resource(testcase.HttpCaseView, '/case/<int:uid>')
api.add_resource(testcase.HttpStepView, '/step/<int:uid>')
