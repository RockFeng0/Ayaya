#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.app.case.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.app.case.views,  v1.0 2019年4月12日
    FROM:   2019年4月12日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import datetime
from flask import request, jsonify
from flask_login import login_required
from flask.views import MethodView

from rman.app import APP_ENV
from rman.app.testset import testset
from rman.app.project.models import Project, TestsetProjectRelation
from rman.app.testset.models import TestSet
from rman.app.httpcase.models import HttpCase, CaseRecord, db

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_project_query():
    return db.session.query(Project)

def get_tset_query():
    return db.session.query(TestSet)

def get_relation_query():
    return db.session.query(TestsetProjectRelation)

def get_tset_join_project_query():    
    return db.session.query(TestSet, Project)\
        .join(TestsetProjectRelation,TestSet.id == TestsetProjectRelation.test_set_id)\
        .join(Project, TestsetProjectRelation.project_id == Project.id)

def get_httpcase_query():
    return db.session.query(HttpCase)

@testset.route("/get_distinct", methods=["GET"])
def distinct_col():
    # GET /testset/get_distinct?tester=xxxx    
    param = dict(request.args.items())  
    _query = get_tset_query()    
    conditions = {i: param.get(i) for i in ('name', 'responsible', 'tester', 'type') if param.get(i)}    
    lines  = _query.filter_by(**conditions).with_entities(TestSet.name, TestSet.responsible, TestSet.tester, TestSet.type).distinct().all()   
    
    result = [{"name": line[0], "responsible": line[1], "tester": line[2], "type": line[3],} for line in lines if line]
    return jsonify(get_result(result, message = "get all distinct data success."))

class TestSetView(MethodView):
    
    def get(self):
        # GET /manager?page=1&size=10&tset_?=?&proj_?=?
        # 获取指定项目下的所有testset: GET /manager?page=1&size=10&proj_id=1
        # 获取所有 api: GET /manager?page=1&size=10&tset_type=api
        # 获取所有 suite: GET /manager?page=1&size=10&tset_type=suite
        param = dict(request.args.items())
        _query_tset_join_project = get_tset_join_project_query()
        
        tset_conditions = {getattr(TestSet, i) == param.get("tset_%s" %i) for i in ('id', 'name', 'responsible', 'tester', 'type') if param.get("tset_%s" %i)}
        proj_conditions = {getattr(Project, i) == param.get("proj_%s" %i) for i in ('id', 'name', 'module') if param.get("proj_%s" %i)}
        conditions = tset_conditions.union(proj_conditions)
        base_conditions = _query_tset_join_project.filter(*conditions).order_by(TestSet.update_time.desc())
        
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "testsets":[]}
               
        for pg in pagination.items:            
            tset_data = pg.TestSet
            proj_data = pg.Project
            _tset = {
                "id":tset_data.id,
                "name": tset_data.name, 
                "desc":tset_data.desc, 
                "responsible": tset_data.responsible,
                "tester": tset_data.tester,
                "type": tset_data.type,
                "suite_def": tset_data.suite_def,
                "project_name": proj_data.name,
                "project_module": proj_data.module,
                   
                "c_time": tset_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": tset_data.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["testsets"].append(_tset)
        
        return jsonify(get_result(result, message = "Query all data success in page: {0} size: {1}.".format(page, size)))
    
    def post(self):
        # POST /manager        
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_tset_query()
        _query_project = get_project_query()       
        now = datetime.datetime.now()
        
        try:
            
            for param in ("name", "type", "project_name", "project_module"):
                _param = j_param.get(param)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'Parameter [{0}] should not be null.'.format(param)))
                
                if param == 'type':
                    if not _param.lower() in ('api', 'suite', 'case'):
                        return jsonify(get_result("", status = False, message = 'Parameter [type] should be in (api, suite, case).'))
                    
                    if _param == 'suite' and not j_param.get('suite_def'):
                        return jsonify(get_result("", status = False, message = "Not found parameter 'suite_def'"))
                  
                    
            status = True
            tset_data = _query.filter_by(name = j_param.get("name")).first()
            project_data = _query_project.filter_by(name = j_param.get("project_name"), module = j_param.get("project_module")).first()
            
            if tset_data:
                status = False
                message = "'%s' already exists." %j_param.get("name")
            
            elif not project_data:
                status = False
                message = "Unknow project[{0}] with module[{1}]".format(j_param.get("project_name"), j_param.get("project_module"))
                            
            else:
                _testset = TestSet(j_param.get("name"),
                     j_param.get("desc",""), 
                     j_param.get("responsible",'administrator'),
                     j_param.get("tester",'administrator'),
                     j_param.get("type"),
                     j_param.get("suite_def"),
                     now, now)                
                db.session.add(_testset)
                db.session.commit()
                
                _tset_relation = TestsetProjectRelation(project_data.id, _testset.id, now, now)
                db.session.add(_tset_relation) 
                               
                message = "add success."
                db.session.flush()
                db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /manager?tset_id=32342
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_tset_query()                
        now = datetime.datetime.now()
        
        try: 
            tset_data = _query.filter_by(id = param.get("tset_id")).first()
                                    
            if not tset_data:
                message = "do not have the testset with tset_id({})".format(param.get("tset_id"))
                return jsonify(get_result("", status = False, message = message))
            
            if 'type' in j_param:
                _param = j_param.get('type')
                if not _param.lower() in ('api', 'suite', 'case'):
                    return jsonify(get_result("", status = False, message = 'Parameter [type] should be in (api, suite, case).'))
                                    
                if _param == 'suite' and not j_param.get('suite_def'):
                    return jsonify(get_result("", status = False, message = "Parameter [suite_def] should not be null."))                  
                            
            _ = [setattr(tset_data, i, j_param.get(i,"")) for i in ["name", "desc", "responsible", "tester", "type", "suite_def"] if j_param.get(i)]                             
            tset_data.update_time = now
                                    
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
        _query = get_tset_query()
        _query_relation = get_relation_query()
        _query_httpcase = get_httpcase_query()
        
        try:
            tset_ids = param.get("ids").split(',')        
            result = {"delete_result":{}}
            for tset_id in tset_ids:
                tset_data = _query.filter_by(id = tset_id).first()            
                        
                if tset_data:
                    db.session.delete(tset_data)
                    
                    # delete tset_project_relation
                    relation_datas = _query_relation.filter_by(test_set_id = tset_id).all()
                    for relation_data in relation_datas:            
                        db.session.delete(relation_data)
                    
                    # delete tset_requests
                    httpcases = _query_httpcase.filter_by(test_set_id = tset_id).all()
                    for _httpcase in httpcases:            
                        db.session.delete(_httpcase)
                                    
                    db.session.commit()
                    result["delete_result"][tset_id] = True                    
                else:
                    result["delete_result"][tset_id] = False
            
            status = False if False in result["delete_result"].values() else True        
            message = "delete success."    
        except Exception as e:
            result = ''
            message = str(e)
            status = False
            
        return jsonify(get_result(result, status = status,message = message))
    
    
if APP_ENV == "production":
    _tset_view_manager = login_required(TestSetView.as_view('tset_view_manager'))    
else:
    _tset_view_manager = TestSetView.as_view('tset_view_manager')      

testset.add_url_rule('/manager', view_func=_tset_view_manager)

