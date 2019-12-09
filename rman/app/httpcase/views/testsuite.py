#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.httpcase.views.testsuite

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.httpcase.views.testsuite,  v1.0 2019年7月5日
    FROM:   2019年7月5日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import datetime, json
from flask import request, jsonify
from flask_login import login_required
from flask.views import MethodView

from rman.app import APP_ENV, get_result
from rman.app.httpcase import httpcase
from rman.app.httpcase.models import db,HttpCaseQuerys, HttpCase
from rman.app.manager.models import TestApis, TestSuiteApiRelation, TestSuites


class TestApiView(MethodView):
    
    def get(self):
        #/suite?pj_id=xx
        param = dict(request.args.items())        
        _query_project = HttpCaseQuerys.t_project()
        _query_suite = HttpCaseQuerys.t_suite()
        _query_suite_relation_api = HttpCaseQuerys.j_suite_relation_api()
        
        project_id = param.get("pj_id")
        if not project_id:
            return jsonify(get_result("", status = False, message = 'Parameter [pj_id] should not be null.'))
        
        proj_data = _query_project.filter_by(id = project_id).first()
        if not proj_data:
            return jsonify(get_result("", status = False, message = 'Testproject [id={0}] not exist.'.format(project_id)))
        
        result = {
            "pj_id": project_id,
            "pj_name": proj_data.name,
            "pj_module_name": proj_data.module,
            "tset_name": "administrator",
            "tset_responsible": "administrator",
            "tset_tester": "administrator",            
            "suites": [],
        }
        suite_datas = _query_suite.filter_by(project_id = project_id).all()
        
        for suite_data in suite_datas:
            _suite = {
                "id":  suite_data.id,
                "suite_def": suite_data.suite_def,
                "cases": [],
            }
            case_datas = _query_suite_relation_api.filter(TestSuiteApiRelation.suite_id == suite_data.id).all()
            for name, api_def in case_datas:                
                _suite["cases"].append({"name": name, "api": api_def})            
            result["suites"].append(_suite)
        
        return jsonify(get_result(result, message = "Query all data  success."))
    
    def post(self):
        #/suite?pj_id=xx
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        now = datetime.datetime.now()
           
        _query_suite = HttpCaseQuerys.t_suite()
        _query_api = HttpCaseQuerys.t_api()
        _query_project = HttpCaseQuerys.t_project()
                
        project_id = param.get("pj_id")
        if not _query_project.filter_by(id = project_id).first():
            return jsonify(get_result("", status = False, message = 'Testproject [id={0}] not exist.'.format(project_id)))
               
        suite_def= j_param.get("suite_def")
        cases= j_param.get("cases", [])
        if not suite_def or not cases:
            return jsonify(get_result("", status = False, message = "Parameter ['suite_def', 'cases'] should not be null in Testsuite."))
        
        # 同一项目，suite_def 唯一
        if _query_suite.filter_by(project_id = project_id, suite_def = suite_def).first():
            return jsonify(get_result("", status = False, message = 'Testsuite [suite_def={0}] already exists in Testproject[id={1}].'.format(suite_def, project_id)))
        
        try:
            if isinstance(cases, str):
                cases = json.loads(cases)
        except:
            pass
        
        if not isinstance(cases, list):
            return jsonify(get_result("", status = False, message = "Parameter 'cases' need a list type."))
            
        for case in cases:
            if not isinstance(case, dict):
                return jsonify(get_result("", status = False, message = "Parameter 'cases' need a content a dict type."))
            
        _relations = []
        names = []
        for case in cases:         
            name = case.get("name")
            api_def = case.get("api")
                        
            _api = _query_api.filter_by(api_def = api_def).first()
            if not _api:
                return jsonify(get_result("", status = False, message = "Not found the [api={0}] in TestApi.".format(api_def)))
                        
            if not name:
                return jsonify(get_result("", status = False, message = "Key 'name' should not be '{0}' in the parameter 'cases'.".format(name)))
            
            _relations.append((name, _api.id))
            names.append(name)
        
        if len(set(names)) != len(names):
            return jsonify(get_result("", status = False, message = "Found not unique 'name' in parameter 'cases'."))
                            
        suite_kwargs = {"suite_def": suite_def, "project_id": project_id, "create_time": now, "update_time":now}
        _suite = TestSuites(**suite_kwargs)
        db.session.add(_suite)
        db.session.flush()  
        
        for name, api_id in _relations:
            _relation = TestSuiteApiRelation(api_id = api_id, suite_id = _suite.id, name = name, create_time=now, update_time = now)
            db.session.add(_relation)
        db.session.flush()
        
        db.session.commit()
        return jsonify(get_result("", message = "add success."))
    
    def put(self):
        #/suite?tsuite_id=xx
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        now = datetime.datetime.now()
           
        _query_suite = HttpCaseQuerys.t_suite()
        _query_api = HttpCaseQuerys.t_api()
        _query_suite_api_relation = HttpCaseQuerys.t_suite_api_relation()
                
        tsuite_id = param.get("tsuite_id")
        tsuite_data = _query_suite.filter_by(id = tsuite_id).first()
        if not tsuite_data:
            return jsonify(get_result("", status = False, message = 'Testsuite [id={0}] not exist.'.format(tsuite_id)))
        
        cases= j_param.get("cases")
                
        try:
            if isinstance(cases, str):
                cases = json.loads(cases)
        except:
            pass
        
        # 更新的时候， cases不能是空的list
        if not cases:
            return jsonify(get_result("", status = False, message = "Parameter 'cases' should not be null in Testsuite."))
        
        if not isinstance(cases, list):
            return jsonify(get_result("", status = False, message = "Parameter 'cases' need a list type."))
            
        for case in cases:
            if not isinstance(case, dict):
                return jsonify(get_result("", status = False, message = "Parameter 'cases' need a content a dict type."))
            
        _relations = []
        names = []
        for case in cases:            
            name = case.get("name")
            api_def = case.get("api")
                        
            _api = _query_api.filter_by(api_def = api_def).first()
            if not _api:
                return jsonify(get_result("", status = False, message = "Not found the [api={0}] in TestApi.".format(api_def)))
                        
            if not name:
                return jsonify(get_result("", status = False, message = "Key 'name' should not be '{0}' in the parameter 'cases'.".format(name)))
            
            _relations.append((name, _api.id))
            names.append(name)
        
        if len(set(names)) != len(names):
            return jsonify(get_result("", status = False, message = "Found not unique 'name' in parameter 'cases'."))
        
        # delete old relation
        _relation_datas = _query_suite_api_relation.filter_by(suite_id = tsuite_id).all()        
        for _relation_data in _relation_datas:
            db.session.delete(_relation_data)
        db.session.flush()
        
        # add new relation
        for name, api_id in _relations:
            _relation = TestSuiteApiRelation(api_id = api_id, suite_id = tsuite_id, name = name, create_time=now, update_time = now)            
            db.session.add(_relation)
        db.session.flush()
            
        db.session.commit()
        return jsonify(get_result("", message = "update success."))
    
    def delete(self):
        #/suite?tsuite_id=xx
        param = dict(request.args.items())
        
        _query_suite = HttpCaseQuerys.t_suite()        
        _query_suite_api_relation = HttpCaseQuerys.t_suite_api_relation()
                
        tsuite_id = param.get("tsuite_id")
        tsuite_data = _query_suite.filter_by(id = tsuite_id).first()
        if tsuite_data:
            db.session.delete(tsuite_data)
        
        _relation_datas = _query_suite_api_relation.filter_by(suite_id = tsuite_id).all()        
        for _relation_data in _relation_datas:
            db.session.delete(_relation_data)
                                        
        db.session.commit()
        return jsonify(get_result("", message = "delete success."))
    
if APP_ENV == "production":
    _view = login_required(TestApiView.as_view('tsuite_view_manager'))    
else:
    _view = TestApiView.as_view('tsuite_view_manager')      

httpcase.add_url_rule('/suite', view_func=_view)