#! python3
# -*- encoding: utf-8 -*-
"""
Rough version history:
v1.0    Original version to use
********************************************************************
    @AUTHOR:  罗科峰
    MAIL:     luokefengds@chinamobile.com
    RCS:      httpcase.py,  v1.0 2020/9/4
    FROM:     2020/9/4
********************************************************************

"""

from flask import Blueprint
from flask_restful import Api
from rman.app.resources.httpcases.configs import InterfaceConfigsView
from rman.app.resources.httpcases.testsuites import TestSuitesView
from rman.app.resources.httpcases.testsets import TestSetsView
from rman.app.resources.httpcases.testapis import TestApisView

httpcases = Blueprint('httpcases', __name__)

api = Api(httpcases)
api.add_resource(InterfaceConfigsView, '/configs')
api.add_resource(TestSuitesView, '/testsuites')
api.add_resource(TestSetsView, '/testsets')
api.add_resource(TestApisView, '/testapis')
