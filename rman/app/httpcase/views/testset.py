#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.httpcase.views.testset

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.httpcase.views.testset,  v1.0 2019年7月5日
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
from rman.app.manager.models import TestProject, TestSet, TestCases


class HttpCaseView(MethodView):
    
    def get(self):
        # GET /tset?page=1&size=10&tset_?=?&pj_?=?
        param = dict(request.args.items())
        _query = HttpCaseQuerys.j_project_set()
        _query_case = HttpCaseQuerys.j_tcase_hcase()
        
        tset_like_conditions = {getattr(TestSet,i).like("{0}%".format(param.get("tset_%s" %i))) for i in ('name',) if param.get("tset_%s" %i)}
        pj_like_conditions = {getattr(TestProject,i).like("{0}%".format(param.get("pj_%s" %i))) for i in ('name','module') if param.get("pj_%s" %i)}
        like_conditions =  tset_like_conditions.union(pj_like_conditions)
        
        tset_conditions = {getattr(TestSet,i) == param.get("tset_%s" %i) for i in ('id', 'responsible', 'tester') if param.get("tset_%s" %i)}
        pj_conditions = {getattr(TestProject, i) == param.get("pj_%s" %i) for i in ('id',) if param.get("pj_%s" %i)}
        equal_conditions = tset_conditions.union(pj_conditions)
        
        conditions = like_conditions.union(equal_conditions)                
        base_conditions = _query.filter(*conditions).order_by(TestSet.update_time.desc())
                
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "tsets":[]}
        for pg in pagination.items:
            tset_data = pg.TestSet
            pj_data = pg.TestProject
            
            _tset = {                
                "pj_id": pj_data.id,
                "pj_name": pj_data.name,
                "pj_module_name": pj_data.module,
                "tset_id": tset_data.id,
                "tset_name": tset_data.name,
                "tset_responsible": tset_data.responsible,
                "tset_tester": tset_data.tester,                
                "tset_c_time": tset_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "tset_u_time": tset_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "cases": [],
            }
                        
            cases = _query_case.filter(TestCases.test_set_id == tset_data.id).all()   
            
            for cs in cases:
                tc_data = cs.TestCases
                hc_data = cs.HttpCase
                
                _case = {
                    "id": tc_data.id,
                    "name": tc_data.name,
                    "call_api": tc_data.call_api,
                    "call_suite": tc_data.call_suite,
                }
                _case["url"] = hc_data.url if hc_data else ""
                _case["method"] = hc_data.method if hc_data else ""
                _case.update({i: json.loads(getattr(hc_data, i)) if hc_data else {} for i in ("glob_var", "glob_regx", "headers", "body", "files")})
                _case.update({i: json.loads(getattr(hc_data, i))  if hc_data else [] for i in ("pre_command", "post_command", "verify")})
                    
                _tset["cases"].append(_case)
            result["tsets"].append(_tset)
        
        return jsonify(get_result(result, message = "Query all data  success in page: {0} size: {1}.".format(page, size)))
        
    def post(self):     
        # POST /tset    添加 TestSet
        # POST /tset?tset_id=xx      添加 TestCase
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        now = datetime.datetime.now()
        
        _query_tcase = HttpCaseQuerys.t_case()
        _query_hcase = HttpCaseQuerys.t_hcase()
        _query_project = HttpCaseQuerys.t_project()
        _query_tset = HttpCaseQuerys.t_set()
        
        status = True
        try:
            tset_id = param.get("tset_id")
            
            if tset_id:
                _tset = _query_tset.filter_by(id = tset_id).first()
                if not _tset:
                    return jsonify(get_result("", status = False, message = 'Testset [tset_id={0}] not exist.'.format(tset_id)))
                
                name = j_param.get("name")
                call_suite = j_param.get("call_suite", "")
                call_api = j_param.get("call_api", "")
                
                if not name:
                    return jsonify(get_result("", status = False, message = 'Parameter [name] should not be null.'))
                
                if _query_tcase.filter_by(name = name, test_set_id = tset_id).first():
                    return jsonify(get_result("", status = False, message = 'Testcase [name={0}] already exists in Testset[id={1}].'.format(name, tset_id)))
                
                tcase_kwargs = {
                    "name": name,
                    "call_suite": call_suite,
                    "call_api": call_api,
                    "test_set_id": tset_id,
                    "call_manunal_id": None,
                    "create_time": now,
                    "update_time": now,
                }                                    
                if not call_api and not call_suite:                     
                    url = j_param.get("url", "")
                    method = j_param.get("method", "")
                    if not url or not method:
                        return jsonify(get_result("", status = False, message = 'Parameter [url, method] should not be null.'))
                    
                    hcase_kwargs = {}
                    _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,{}))}) for i in ("glob_var", "glob_regx", "headers", "body", "files")]   
                    _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,[]))}) for i in ("pre_command", "post_command", "verify")]  
                    hcase_kwargs.update({"url":url, "method":method, "create_time": now, "update_time":now})                
                    _httpcase = HttpCase(**hcase_kwargs)                    
                    db.session.add(_httpcase)
                    db.session.flush()                    
                    tcase_kwargs["call_manunal_id"] = _httpcase.id
                                        
                _testcase = TestCases(**tcase_kwargs)
                db.session.add(_testcase)
                db.session.commit()
                
            else:                
                pj_name = j_param.get("pj_name")
                pj_module_name = j_param.get("pj_module_name")
                pj_comment = j_param.get("pj_comment", "")
                
                tset_name = j_param.get("tset_name")
                tset_desc = j_param.get("desc", "")
                tset_responsible = j_param.get("tset_responsible", "")
                tset_tester = j_param.get("tset_tester", "")
                
                if not pj_name or not pj_module_name or not tset_name:
                    return jsonify(get_result("", status = False, message = 'Parameter [pj_name, pj_module_name, tset_name] should not be null.'))
                                
                _pj = _query_project.filter_by(name = pj_name, module = pj_module_name).first()
                if not _pj:
                    _pj = TestProject(name = pj_name, module = pj_module_name, comment=pj_comment, create_time = now, update_time = now)
                    db.session.add(_pj)
                    db.session.commit()
                
                _tset = _query_tset.filter_by(name = tset_name, project_id = _pj.id).first()
                if _tset:
                    # 同一项目，不可重名
                    return jsonify(get_result("", status = False, message = "Testset '{0}' already exist， Can't override it.".format(tset_name)))                
                _tset = TestSet(name = tset_name, desc = tset_desc,responsible = tset_responsible, tester = tset_tester, project_id = _pj.id, create_time = now, update_time = now)
                db.session.add(_tset)
                db.session.commit()            
                          
            message = "add success."
            db.session.flush()
            db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))
     
    def put(self):
        # PUT /tset?tset_id=32342    更新 TestSet  的 name、desc、tester
        # PUT /tset?tcase_id=32342    更新 TestCase
        param = dict(request.args.items())
        if not param.get("tset_id") and not param.get("tcase_id"):
            return jsonify(get_result("", status = False, message = "Not found parameter 'tset_id' or 'tcase_id'."))
        
        j_param = request.json if request.data else request.form.to_dict()
        _query_tset = HttpCaseQuerys.t_set()
        _query_tcase = HttpCaseQuerys.t_case()
        _query_hcase = HttpCaseQuerys.t_hcase()
        now = datetime.datetime.now()
        
        try: 
            tset_data = _query_tset.filter_by(id = param.get("tset_id")).first()
            tcase_data = _query_tcase.filter_by(id = param.get("tcase_id")).first()
            
            if tset_data:
                name = j_param.get("tset_name")
                if not name:
                    return jsonify(get_result("", status = False, message = 'Parameter [tset_name] should not be null.'))
                
                if tset_data.name != name and _query_tset.filter(TestSet.project_id == tset_data.project_id, TestSet.name == name).first():
                    # 同一项目，测试集不可重名
                    return jsonify(get_result("", status = False, message = "Testset '{0}' already exist in Project id={1}. Can't override it.".format(name, tset_data.project_id)))
                
                tset_data.name = j_param.get("tset_name")
                tset_data.desc = j_param.get("desc")
                tset_data.tester = j_param.get("tset_tester")                             
                tset_data.update_time = now
            
            elif tcase_data:                
                name = j_param.get("name")
                call_suite = j_param.get("call_suite", "")
                call_api = j_param.get("call_api", "")
                
                if not name:
                    return jsonify(get_result("", status = False, message = 'Parameter [name] should not be null.'))
                
                if tcase_data.name != name and _query_tcase.filter_by(test_set_id = tcase_data.test_set_id, name = name).first():
                    # 同一测试集，用例不可重名
                    return jsonify(get_result("", status = False, message = "Testcase '{0}' already exist in Testset id={1}， Can't override it.".format(name, tcase_data.test_set_id))) 
                
                tcase_data.name = name             
                _httpcase = _query_hcase.filter_by(id = tcase_data.call_manunal_id).first()
                if not call_api and not call_suite:                     
                    url = j_param.get("url", "")
                    method = j_param.get("method", "")
                    if not url or not method:
                        msg = 'Parameter [url, method] should not be null, if without [call_api or call_suite].'
                        return jsonify(get_result("", status = False, message = msg))
                    
                    hcase_kwargs = {}
                    _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,{}))}) for i in ("glob_var", "glob_regx", "headers", "body", "files")]   
                    _ = [hcase_kwargs.update({i: json.dumps(j_param.get(i,[]))}) for i in ("pre_command", "post_command", "verify")]  
                    hcase_kwargs.update({"url":url, "method":method, "update_time":now})
                                        
                    if _httpcase:
                        _ = [setattr(_httpcase, k, v) for k,v in hcase_kwargs.items()]
                    else:
                        hcase_kwargs["create_time"] = now
                        _httpcase = HttpCase(**hcase_kwargs)
                        db.session.add(_httpcase)
                        db.session.commit()
                        
                        tcase_data.call_api = ""
                        tcase_data.call_suite = ""
                        tcase_data.call_manunal_id = _httpcase.id
                        
                elif call_api:
                    tcase_data.call_api = call_api                    
                    tcase_data.call_suite = ""
                    tcase_data.call_manunal_id = None
                    if _httpcase:
                        db.session.delete(_httpcase)
                    tcase_data.update_time = now
                    
                elif call_suite:                    
                    tcase_data.call_api = ""                    
                    tcase_data.call_suite = call_suite
                    tcase_data.call_manunal_id = None
                    if _httpcase:
                        db.session.delete(_httpcase)
                    tcase_data.update_time = now
                                                     
            status = True
            message = "update success."
            db.session.flush()
            db.session.commit()            
        except Exception as e:
            message = str(e)
            status = False
     
        return jsonify(get_result("", status = status, message = message))       
                 
    def delete(self):
        # DELETE /tset?tset_ids='1,2,3,4,5'    删除 TestSet
        # DELETE /tset?tcase_ids='1,2,3,4,5'   删除TestCases
        param = dict(request.args.items())
        
        _query_tset = HttpCaseQuerys.t_set()
        _query_tcase = HttpCaseQuerys.t_case()
        _query_hcase = HttpCaseQuerys.t_hcase()
                
        try:            
            tset_ids = param.get("tset_ids","").split(',')            
            tcase_ids = param.get("tcase_ids","").split(',')
            
            for tcase_id in tcase_ids:
                tcase_data = _query_tcase.filter_by(id = tcase_id).first()
                if not tcase_data:
                    continue
                         
                # delete HttpCases
                _hcase_data = _query_hcase.filter_by(id = tcase_data.call_manunal_id).first()
                if _hcase_data:
                    db.session.delete(_hcase_data)
                
                # delete TestCases
                db.session.delete(tcase_data)            
            
            for tset_id in tset_ids:
                tset_data = _query_tset.filter_by(id = tset_id).first()            
                         
                if not tset_data:
                    continue
                
                # delete TestSet
                db.session.delete(tset_data)
                
                # delete TestCases                    
                _tcase_datas = _query_tcase.filter_by(test_set_id = tset_id).all()
                for _tcase_data in _tcase_datas:
                                           
                    # delete HttpCases
                    _hcase_data = _query_hcase.filter_by(id = _tcase_data.call_manunal_id).first()
                    if _hcase_data:
                        db.session.delete(_hcase_data)                    
                                            
                    db.session.delete(_tcase_data)
                        
            db.session.commit()
             
            status = True      
            message = "delete success."    
        except Exception as e:
            message = str(e)
            status = False
             
        return jsonify(get_result('', status = status,message = message))
    
    

if APP_ENV == "production":
    _httpcase_view_manager = login_required(HttpCaseView.as_view('httpcase_view_manager'))
else:
    _httpcase_view_manager = HttpCaseView.as_view('httpcase_view_manager')  

httpcase.add_url_rule('/tset', view_func=_httpcase_view_manager)