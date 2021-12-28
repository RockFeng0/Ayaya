#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.httpcase.views.testapi

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.httpcase.views.testapi,  v1.0 2019年7月5日
    FROM:   2019年7月5日
********************************************************************
======================================================================

Provide a function for the automation test

'''
import datetime, json
from flask import request, jsonify
from flask_login import login_required
from flask.views import MethodView

from rman.app import APP_ENV
from rman.app.routes.api_0_0.httpcase import httpcase
from rman.app.routes.api_0_0.httpcase.models import db,HttpCaseQuerys, HttpCase
from rman.app.routes.api_0_0.manager.models import TestApis, TestSuiteApiRelation, TestSuites


def get_result(result, status=True, message="success"):
    return {"status": status, "message": message, "result": result}


class TestApiView(MethodView):
    
    def get(self):
        #/api?pj_id=xx
        param = dict(request.args.items())        
        _query_project = HttpCaseQuerys.t_project()
        _query_api = HttpCaseQuerys.j_api_hcase()
        
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
            "apis": []
        }
        api_datas = _query_api.filter(TestApis.project_id == project_id).all()
        
        for pg in api_datas:
            api_data = pg.TestApis
            hc_data = pg.HttpCase
                        
            _api = {i: json.loads(getattr(hc_data, i)) for i in ("glob_var", "glob_regx", "headers", "body", "files", "pre_command", "post_command", "verify")}
            _api["id"] = api_data.id
            _api["api_def"] = api_data.api_def
            _api["url"] = hc_data.url
            _api["method"] = hc_data.method
            
            result["apis"].append(_api)
        
        return jsonify(get_result(result, message = "Query all data  success."))
    
    def post(self):
        #/api?pj_id=xx
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        now = datetime.datetime.now()
           
        _query_api = HttpCaseQuerys.t_api()
        _query_project = HttpCaseQuerys.t_project()
                
        project_id = param.get("pj_id")
        if not _query_project.filter_by(id = project_id).first():
            return jsonify(get_result("", status = False, message = 'Testproject [id={0}] not exist.'.format(project_id)))
                
        api_def= j_param.get("api_def")        
        url = j_param.get("url", "")
        method = j_param.get("method", "")
        if not api_def or not url or not method:
            return jsonify(get_result("", status = False, message = 'Parameter [api_def, url, method] should not be null.'))
        
        api_def_data = _query_api.filter_by(project_id = project_id, api_def = api_def).first()
        if api_def_data:
            return jsonify(get_result("", status = False, message = 'Testapi [api_def={0}] already exists in Testproject[id={1}].'.format(api_def, project_id)))
        
        hcase_kwargs = {}
        _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,{}))}) for i in ("glob_var", "glob_regx", "headers", "body", "files")]   
        _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,[]))}) for i in ("pre_command", "post_command", "verify")]  
        hcase_kwargs.update({"url":url, "method":method, "create_time": now, "update_time":now})                
        _httpcase = HttpCase(**hcase_kwargs)                    
        db.session.add(_httpcase)
        db.session.flush()  
        
        tapi_kwargs = {
            "api_def": api_def,
            "call_manunal_id": _httpcase.id,
            "project_id": project_id,
            "create_time": now, 
            "update_time":now
        }
        _api = TestApis (**tapi_kwargs)        
        db.session.add(_api)
        db.session.commit()            
                          
        return jsonify(get_result("", message = "add success."))
    
    def put(self):
        #/api?tapi_id=xx
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        now = datetime.datetime.now()
           
        _query_api = HttpCaseQuerys.t_api()
        _query_hcase = HttpCaseQuerys.t_hcase()
                
        tapi_id = param.get("tapi_id")
        tapi_data = _query_api.filter_by(id = tapi_id).first()
        if not tapi_data:
            return jsonify(get_result("", status = False, message = 'TestApi not exist with parameter [tapi_id={0}].'.format(tapi_id)))
                
        hcase_kwargs = {}       
        api_def= j_param.get("api_def") 
        url = j_param.get("url", "")
        method = j_param.get("method", "")
        if not api_def or not url or not method:
            return jsonify(get_result("", status = False, message = 'Parameter [api_def, url, method] should not be null.'))
        
        tapi_data.api_def = api_def
        tapi_data.update_time = now
        _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,{}))}) for i in ("glob_var", "glob_regx", "headers", "body", "files")]   
        _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,[]))}) for i in ("pre_command", "post_command", "verify")]
        hcase_kwargs.update({"url":url, "method":method, "update_time":now})
        
        tcase_data = _query_hcase.filter_by(id=tapi_data.call_manunal_id).first()
        _ = [setattr(tcase_data, k, v) for k,v in hcase_kwargs.items()]        
        db.session.flush()
        db.session.commit()           
                          
        return jsonify(get_result("", message = "update success."))
    
    def delete(self):
        # /api?tapi_id=xx
        param = dict(request.args.items())
        
        _query_tapi = HttpCaseQuerys.t_api()
        _query_hcase = HttpCaseQuerys.t_hcase()
                
        tapi_id = param.get("tapi_id")
        
        tapi_data = _query_tapi.filter_by(id = tapi_id).first()        
        if not tapi_data:
            return jsonify(get_result("", message = "delete success."))
        
        hcase_data = _query_hcase.filter_by(id = tapi_data.call_manunal_id).first()
        print(hcase_data)
        if hcase_data:
            db.session.delete(hcase_data)
            
        db.session.delete(tapi_data)                        
        db.session.commit()
        return jsonify(get_result("", message = "delete success."))
    
if APP_ENV == "production":
    _view = login_required(TestApiView.as_view('tapi_view_manager'))    
else:
    _view = TestApiView.as_view('tapi_view_manager')      

httpcase.add_url_rule('/api', view_func=_view)