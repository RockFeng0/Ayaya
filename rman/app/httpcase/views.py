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

class HttpCaseView(MethodView):
    
    def get(self):
        # GET /manager?page=1&size=10&tset_?=?&hcase_?=?
        # 获取指定测试集所有接口测试用例: GET /manager?page=1&size=10&tset_id=1
        # 获取指定测试集所有get请求: GET /manager?page=1&size=10&tset_id=1&hcase_method=get
        print("!!!!")
        param = dict(request.args.items())
        _query_hcase_join_tset = get_hcase_join_tset_query()
        
        tset_conditions = {getattr(TestSet,i) == param.get("tset_%s" %i) for i in ('id', 'name', 'responsible', 'tester', 'type') if param.get("tset_%s" %i)}
        http_conditions = {getattr(HttpCase, i) == param.get("hcase_%s" %i) for i in ('id', 'name', 'url', 'method', 'api_name', 'suite_name') if param.get("hcase_%s" %i)}
        conditions = tset_conditions.union(http_conditions)                
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
        # POST /manager?tset_id=1&case_mode=?   call_api or call_suite or manunal
        param = dict(request.args.items()) 
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_httpcase_query()
        _query_tset = get_tset_query()       
        now = datetime.datetime.now()
        
        tset_id = param.get("tset_id")
        case_mode = param.get("case_mode")
        tset_data = _query_tset.filter_by(id = tset_id).first()
        
        try:
            if case_mode == "manunal":
                for param in ("url", "method"):
                    _param = j_param.get(param)
                    if not _param:
                        return jsonify(get_result("", status = False, message = 'Parameter [{0}] should not be null.'.format(param)))
                        
            status = True            
            if not tset_data:
                status = False
                message = "Not found the testset with id: {0}".format(tset_id)
                            
            else:
                # string:  name, suite_name, api_name, func,url, method
                # dict:    glob_var, glob_regx, headers, body
                # list:    pre_command, post_command, verify                
                
                args = []                
                for k,v in j_param.items():
                    print(k,v)
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
        now = datetime.datetime.now()
        
        try:
             
            httpcase_data = _query.filter_by(id = param.get("id")).first()
            
            if not httpcase_data:
                message = "do not have the httpcase with id({})".format(param.get("id"))
                return jsonify(get_result("", status = False, message = message))
                        
            _ = [setattr(httpcase_data, i, j_param.get(i)) for i in ("name", "suite_name", "api_name", "func","url", "method", "case_mode") if hasattr(httpcase_data, i) and j_param.get(i)]
            _ = [setattr(httpcase_data, i, json.dumps(j_param.get(i))) for i in("glob_var", "glob_regx", "headers", "body", "files", "pre_command", "post_command", "verify") if hasattr(httpcase_data, i) and j_param.get(i)]            
#             _ = [setattr(httpcase_data, i, json.dumps(j_param.get(i))) for i in j_param.keys() if hasattr(httpcase_data, i) and j_param.get(i)]
            
            httpcase_data.update_time = now
                                    
            status = True
            message = "update success."
            db.session.flush()
            db.session.commit()   
            print(5)           
        except Exception as e:
            message = str(e)
            status = False
        print(6)  
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
    