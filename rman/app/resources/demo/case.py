#! python3
# -*- encoding: utf-8 -*-
"""
Rough version history:
v1.0    Original version to use
********************************************************************
    @AUTHOR:  罗科峰
    MAIL:     luokefengds@chinamobile.com
    RCS:      case.py,  v1.0 2020/9/4
    FROM:     2020/9/4
********************************************************************

"""

from flask_restful import reqparse, abort,  Resource
# from rman.app.routes.api_1_0.demo import demo

CASES = {
    'case1': {'task': 'build an API'},
    'case2': {'task': '?????'},
    'case3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(case_id):
    if case_id not in CASES:
        abort(404, message="Case {} doesn't exist".format(case_id))


parser = reqparse.RequestParser()
parser.add_argument('case_id')


class Case(Resource):
    def get(self, case_id):
        abort_if_todo_doesnt_exist(case_id)
        return CASES[case_id]

    def delete(self, case_id):
        abort_if_todo_doesnt_exist(case_id)
        del CASES[case_id]
        return '', 204

    def put(self, case_id):
        args = parser.parse_args()
        task = {'case_id': args['case_id']}
        CASES[case_id] = task
        return task, 201


