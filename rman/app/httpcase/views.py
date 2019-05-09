#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.httpcase.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.httpcase.views,  v1.0 2018年11月21日
    FROM:   2018年11月21日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import datetime, json
from flask import request, jsonify
from flask_login import login_required
from flask.views import MethodView
from functools import reduce

from rman.app import APP_ENV
from rman.app.httpcase import httpcase
from rman.app.testset.models import TestSet
from rman.app.httpcase.models import HttpCase, CaseRecord, db

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_tset_query():
    return db.session.query(TestSet)

def get_httpcase_query():
    return db.session.query(HttpCase)
        
def get_hcase_join_tset_query():
    return db.session.query(HttpCase, TestSet).join(TestSet, HttpCase.test_set_id == TestSet.id)    

@httpcase.route("/distinct/<column>", methods=["GET"])
def distinct_col(column):
    # GET /httpcase/distinct/func   
    
    if hasattr(HttpCase, column):
        _query = get_httpcase_query()    
        lines  = _query.with_entities(getattr(HttpCase, column)).distinct().all()    
    else:
        return jsonify(get_result("", status=False, message = "unknow column [{0}]".format(column)))
    
    result = [{column: line[0]} for line in lines if line and line[0]]    
    return jsonify(get_result(result, message = "get all distinct data success."))

class HttpCaseView(MethodView):
    
    def get(self):
        # GET /manager?page=1&size=10&tset_?=?&hcase_?=?
        # 获取指定测试集所有接口测试用例: GET /manager?page=1&size=10&tset_id=1
        # 获取指定测试集所有get请求: GET /manager?page=1&size=10&tset_id=1&hcase_method=get        
        param = dict(request.args.items())
        _query_hcase_join_tset = get_hcase_join_tset_query()
        print(param)
        tset_like_conditions = {getattr(TestSet,i).like("{0}%".format(param.get("tset_%s" %i))) for i in ('name',) if param.get("tset_%s" %i)}
        hcase_like_conditions = {getattr(HttpCase,i).like("{0}%".format(param.get("hcase_%s" %i))) for i in ('name','func') if param.get("hcase_%s" %i)}
        like_conditions =  tset_like_conditions.union(hcase_like_conditions)
        
        tset_conditions = {getattr(TestSet,i) == param.get("tset_%s" %i) for i in ('id', 'responsible', 'tester', 'type') if param.get("tset_%s" %i)}
        http_conditions = {getattr(HttpCase, i) == param.get("hcase_%s" %i) for i in ('id', 'url', 'method', 'api_name', 'suite_name') if param.get("hcase_%s" %i)}
        equal_conditions = tset_conditions.union(http_conditions)
        
        conditions = like_conditions.union(equal_conditions)                
        base_conditions = _query_hcase_join_tset.filter(*conditions).order_by(TestSet.update_time.desc())
                
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "httpcases":[]}
        for pg in pagination.items:
            tset_data = pg.TestSet
            hcase_data = pg.HttpCase 
                     
            _case = {
                "testset": {
                    "id":tset_data.id,
                    "name": tset_data.name, 
                    "desc":tset_data.desc, 
                    "responsible": tset_data.responsible,
                    "tester": tset_data.tester,
                    "type": tset_data.type,
                    "suite_def": tset_data.suite_def,
                    },
                "httpcase": {
                    "id":hcase_data.id,
                    "name":hcase_data.name,
                    "case_mode":hcase_data.case_mode,
                    "suite_name":hcase_data.suite_name,
                    "api_name":hcase_data.api_name,
                    "func":hcase_data.func,
                    "glob_var": hcase_data.glob_var,
                    "glob_regx": hcase_data.glob_regx,
                    "pre_command":hcase_data.pre_command,
                    "url":hcase_data.url,
                    "method":hcase_data.method,
                    "headers":hcase_data.headers,
                    "body":hcase_data.body,
                    "files":hcase_data.files,
                    "post_command":hcase_data.post_command,
                    "verify":hcase_data.verify,
                    }, 
                "c_time": hcase_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": hcase_data.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["httpcases"].append(_case)
        
        return jsonify(get_result(result, message = "Query all data  success in page: {0} size: {1}.".format(page, size)))
    
    
    def post(self):
        # POST /manager?tset_id=1
        '''        
            @note:  normal case --> name & case_mode(call_api or call_suite or manunal)
            @note:  suite case --> name & api_name
            @note:  api case --> manunal & func
        '''
        param = dict(request.args.items()) 
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_httpcase_query()
        _query_tset = get_tset_query()
        now = datetime.datetime.now()
        
        tset_id = param.get("tset_id")        
        tset_data = _query_tset.filter_by(id = tset_id).first()
        if not tset_data:
            return jsonify(get_result("", status = False, message = "Not found the data with url parameter [tset_id={0}]".format(tset_id)))        
        
        check_result = self._check_form(tset_data.type, j_param)
        if check_result:
            return jsonify(check_result)
                                           
        try:    
            # string:  name, suite_name, api_name, func,url, method
            # dict:    glob_var, glob_regx, headers, body, files
            # list:    pre_command, post_command, verify 
            
            status = True                          
            
            args = []                
#             for k,v in j_param.items():
#                 print(k,v)
                
            _ = [args.append(j_param.get(i,"")) for i in ("name", "suite_name", "api_name", "func","url", "method", "case_mode")]
            _ = [args.append(json.dumps(j_param.get(i, {}))) for i in ("glob_var", "glob_regx", "headers", "body", "files")]   
            _ = [args.append(json.dumps(j_param.get(i, []))) for i in ("pre_command", "post_command", "verify")]  
                          
            args.extend((tset_data.id,now, now))
            _httpcase = HttpCase(*args)
            
            db.session.add(_httpcase)
            db.session.commit()
                                           
            message = "add success."
            db.session.flush()
            db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /manager?id=32342
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_httpcase_query()
        _query_tset = get_tset_query()              
        now = datetime.datetime.now()
        
        httpcase_data = _query.filter_by(id = param.get("id")).first()
            
        if not httpcase_data:
            message = "do not have the httpcase with id({})".format(param.get("id"))
            return jsonify(get_result("", status = False, message = message))
        
        tset_data = _query_tset.filter_by(id = httpcase_data.test_set_id).first()
        check_result = self._check_form(tset_data.type, j_param)
        if check_result:
            return jsonify(check_result)
        
        try:                        
            _ = [setattr(httpcase_data, i, j_param.get(i)) for i in ("name", "suite_name", "api_name", "func","url", "method", "case_mode") if hasattr(httpcase_data, i) and j_param.get(i)]
            _ = [setattr(httpcase_data, i, json.dumps(j_param.get(i))) for i in("glob_var", "glob_regx", "headers", "body", "files", "pre_command", "post_command", "verify") if hasattr(httpcase_data, i) and j_param.get(i)]            
#             _ = [setattr(httpcase_data, i, json.dumps(j_param.get(i))) for i in j_param.keys() if hasattr(httpcase_data, i) and j_param.get(i)]
            
            httpcase_data.update_time = now
                                    
            status = True
            message = "update success."
            db.session.flush()
            db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))       
    
    def delete(self):
        # DELETE /manager?ids='1,2,3,4,5'
        param = dict(request.args.items())     
        
        _query = get_httpcase_query()
        
        try:
            hcase_ids = param.get("ids").split(',')        
            result = {"delete_result":{}}
            for hcase_id in hcase_ids:
                httpcase_data = _query.filter_by(id = hcase_id).first()
                        
                if httpcase_data:
                    db.session.delete(httpcase_data)
                    db.session.commit()
                    result["delete_result"][hcase_id] = True                    
                else:
                    result["delete_result"][hcase_id] = False
            
            status = False if False in result["delete_result"].values() else True        
            message = "delete done."
        except Exception as e:
            result = ''
            message = str(e)
            status = False
        
        return jsonify(get_result(result, status = status,message = message))
    
    def _check_form(self, case_type, j_param):
                            
        _check_param = ("url", "method")
        _is_real_true = lambda x,y: bool(j_param.get(x)) and bool(j_param.get(y))
        manunal_check = reduce(_is_real_true,_check_param)
        
        name = j_param.get("name")
        case_mode = j_param.get("case_mode")
        func = j_param.get("func")
        api_name = j_param.get("api_name")
                
        if case_type == "api":
            if not manunal_check or not func:
                return get_result("", status = False, message = 'Invalid API-Case without parameter [url or method or func].')
                            
        elif case_type == "case":
            if not name or not case_mode:
                return get_result("", status = False, message = 'Invalid Normal-Case without parameter [name or case_mode].')
            
            if not case_mode in ("call_api", "call_suite", "manunal"):
                return get_result("", status = False, message = 'Invalid Normal-Case, parameter [case_mode] should be in (call_api, call_suite, manunal).')
        
            if case_mode == 'call_api' and not api_name:
                return get_result("", status = False, message = 'Invalid Normal-Case without parameter [api_name].')
            elif case_mode == 'call_suite' and not j_param.get("suite_name"):
                return get_result("", status = False, message = 'Invalid Normal-Case without parameter [suite_name].')
            elif case_mode == 'manunal' and not manunal_check:
                return get_result("", status = False, message = 'Invalid Normal-Case without parameter [url or method].')                
            
        elif case_type == "suite":
            if not name or not api_name:
                return get_result("", status = False, message = 'Invalid Suite-Case without parameter [name or api_name].')
        
        else:
            return get_result("", status = False, message = 'Invalid Http-Case from rtsf-http.')
        
class CaseRecordView(MethodView):
    
    def get(self):
        pass
    
    def post(self):
        pass
    
    def put(self):
        pass

if APP_ENV == "production":
    _httpcase_view_manager = login_required(HttpCaseView.as_view('httpcase_view_manager'))
else:
    _httpcase_view_manager = HttpCaseView.as_view('httpcase_view_manager')  

httpcase.add_url_rule('/manager', view_func=_httpcase_view_manager)
    