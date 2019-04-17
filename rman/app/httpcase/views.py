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

def get_tset_requests_query():
    return db.session.query(HttpCase)
        
def get_requests_join_tset_query():
    return db.session.query(HttpCase, TestSet).join(TestSet, HttpCase.test_set_id == TestSet.id)    

class HttpCaseView(MethodView):
    
    def get(self):
        # GET /manager?page=1&size=10&tset_?=?&http_?=?
        # 获取指定用例所有请求: GET /manager?page=1&size=10&tset_id=1
        # 获取指定用例所有get请求: GET /manager?page=1&size=10&tset_id=1&http_method=get
        
        param = dict(request.args.items())
        _query_requests_join_case = get_requests_join_tset_query()
        
        tset_conditions = {getattr(TestSet,i) == param.get("tset_%s" %i) for i in ('id', 'name', 'responsible', 'tester', 'type') if param.get("tset_%s" %i)}
        http_conditions = {getattr(HttpCase, i) == param.get("http_%s" %i) for i in ('id', 'url', 'method') if param.get("http_%s" %i)}
        conditions = tset_conditions.union(http_conditions)                
        base_conditions = _query_requests_join_case.filter(*conditions).order_by(TestSet.update_time.desc())
                
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "tset_requests":[]}
        for case in pagination.items:
            tset_data = case.Case
            tset_req_data = case.HttpCase           
            _case = {
                "basic": {
                    "id":tset_data.id,
                    "name": tset_data.name, 
                    "desc":tset_data.desc, 
                    "responsible": tset_data.responsible,
                    "tester": tset_data.tester,
                    "type": tset_data.type,
                    "func": tset_data.func,
                    },
                "http": {
                    "glob_var": tset_req_data.glob_var,
                    "glob_regx": tset_req_data.glob_regx,
                    "pre_command":tset_req_data.pre_command,
                    "url":tset_req_data.url,
                    "method":tset_req_data.method,
                    "hearders":tset_req_data.hearders,
                    "body":tset_req_data.body,
                    "post_command":tset_req_data.post_command,
                    "verify":tset_req_data.verify,
                    }, 
                "c_time": tset_req_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": tset_req_data.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["tset_requests"].append(_case)
        
        return jsonify(get_result(result, message = "get all cases_requests success in page: {0} size: {1}.".format(page, size)))
    
    
    def post(self):
        # POST /manager?tset_id=1
        param = dict(request.args.items()) 
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_tset_requests_query()
        _query_case = get_tset_query()       
        now = datetime.datetime.now()
        
        tset_id = param.get("tset_id")
        tset_data = _query_case.filter_by(id = tset_id).first()
                    
        try:
            
            for param in ("url", "method"):
                _param = j_param.get(param)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'HttpCase parameter [{0}] should not be null.'.format(param)))
                                                    
            status = True            
            if not tset_data:
                status = False
                message = "Not found the case with id: {0}".format(tset_id)
                            
#             elif _query.filter_by(tset_id = tset_data.id).first():
#                 status = False
#                 message = "The requests of this tset_id[{0}]  already exists.".format(tset_data.id)
            else:
                _tset_requests = HttpCase(j_param.get("glob_var", '{}'),
                    j_param.get("glob_regx",'{}'), 
                    j_param.get("pre_command",'[]'),
                    j_param.get("url"),
                    j_param.get("method"),
                    j_param.get("hearders", '{}'),
                    j_param.get("body", '{}'),
                    j_param.get("post_command",'[]'),
                    j_param.get("verify",'[]'),
                    tset_data.id,now, now)
                db.session.add(_tset_requests)
                db.session.commit()
                                               
                message = "add tset_requests success."
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
        _query = get_tset_requests_query()                
        now = datetime.datetime.now()
        
        try: 
            tset_requests_data = _query.filter_by(id = param.get("id")).first()
            
            if not tset_requests_data:
                message = "do not have the tset_requests with id({})".format(param.get("id"))
                return jsonify(get_result("", status = False, message = message))
            
            _ = [setattr(tset_requests_data, i, j_param.get(i)) for i in ["url","method","glob_var", "glob_regx", "hearders", "body", "pre_command", "post_command", "verify"] if j_param.get(i)]                
            tset_requests_data.update_time = now
                                    
            status = True
            message = "update tset_requests success."
            db.session.flush()
            db.session.commit()            
        except Exception as e:
            message = str(e)
            status = False
    
        return jsonify(get_result("", status = status, message = message))       
    
    def delete(self):
        # DELETE /manager?id=32342
        param = dict(request.args.items())
        _query = get_tset_requests_query()        
        tset_requests_data = _query.filter_by(id = param.get("id")).first()
        
        if tset_requests_data:
            db.session.delete(tset_requests_data)                            
            db.session.commit()
            status = True
            message = "delete tset_requests success."        
        else:
            status = False
            message = "do not have the tset_requests with id({})".format(param.get("id"))
        return jsonify(get_result("", status = status,message = message))


class CaseRecordView(MethodView):
    
    def get(self):
        pass
    
    def post(self):
        pass
    
    def put(self):
        pass

if APP_ENV == "production":
    _tset_requests_view_manager = login_required(HttpCaseView.as_view('tset_requests_view_manager'))
else:
    _tset_requests_view_manager = HttpCaseView.as_view('tset_requests_view_manager')  

httpcase.add_url_rule('/manager', view_func=_tset_requests_view_manager)
    