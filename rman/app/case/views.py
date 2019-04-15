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
from rman.app.case import case
from rman.app.project.models import Project, CaseProjectRelation
from rman.app.case.models import Case
from rman.app.httptest.models import CaseRequests, CaseRecord, db

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_project_query():
    return db.session.query(Project)

def get_case_query():
    return db.session.query(Case)

def get_relation_query():
    return db.session.query(CaseProjectRelation)

def get_case_join_project_query():    
    return db.session.query(Case, Project)\
        .join(CaseProjectRelation,Case.id == CaseProjectRelation.case_id)\
        .join(Project, CaseProjectRelation.project_id == Project.id)

def get_case_requests_query():
    return db.session.query(CaseRequests)

class CaseView(MethodView):
    
    def get(self):
        # GET /manager?page=1&size=10&case_?=?&proj_?=?
        param = dict(request.args.items())
        _query_case_join_project = get_case_join_project_query()
        
        case_conditions = {getattr(Case, i) == param.get("case_%s" %i) for i in ('id', 'name', 'responsible', 'tester', 'type') if param.get("case_%s" %i)}
        proj_conditions = {getattr(Project, i) == param.get("proj_%s" %i) for i in ('id', 'name', 'module') if param.get("proj_%s" %i)}
        conditions = case_conditions.union(proj_conditions)
        base_conditions = _query_case_join_project.filter(*conditions).order_by(Case.update_time.desc())
                        
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "cases":[]}
               
        for _case in pagination.items:            
            case_data = _case.Case
            proj_data = _case.Project
            _case = {
                "id":case_data.id,
                "name": case_data.name, 
                "desc":case_data.desc, 
                "responsible": case_data.responsible,
                "tester": case_data.tester,
                "case_type": case_data.case_type,
                "func": case_data.func,
                "project_name": proj_data.name,
                "project_module": proj_data.module,
                   
                "c_time": case_data.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": case_data.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["cases"].append(_case)
        
        return jsonify(get_result(result, message = "get all cases success in page: {0} size: {1}.".format(page, size)))
    
    def post(self):
        # POST /manager        
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_query()
        _query_project = get_project_query()       
        now = datetime.datetime.now()
        
        try:
            
            for param in ("name", "case_type", "project_name", "project_module"):
                _param = j_param.get(param)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'Case parameter [{0}] should not be null.'.format(param)))
                
                if param == 'case_type':
                    if not _param.lower() in ('api', 'suite', 'case'):
                        return jsonify(get_result("", status = False, message = 'Case type should be in (api, suite, case).'))
                    
                    if _param == 'case' and j_param.get('func'):
                        return jsonify(get_result("", status = False, message = 'Invaild case with a function name.'))                    
                    
                    if (_param == 'api' or _param == 'suite') and not j_param.get('func'):
                        return jsonify(get_result("", status = False, message = 'Invaild api case or suite case. Do not have relation function.'))
                  
                    
            status = True
            case_data = _query.filter_by(name = j_param.get("name")).first()
            project_data = _query_project.filter_by(name = j_param.get("project_name"), module = j_param.get("project_module")).first()
            
            if case_data:
                status = False
                message = "this case is already exists."
            
            elif not project_data:
                status = False
                message = "Unknow project named '{0}'.".format(j_param.get("project_name"))
                            
            else:
                _case = Case(j_param.get("name"),
                     j_param.get("desc",""), 
                     j_param.get("responsible",'administrator'),
                     j_param.get("tester",'administrator'),
                     j_param.get("case_type"),
                     j_param.get("func"),
                     now, now)                
                db.session.add(_case)
                db.session.commit()
                
                _case_relation = CaseProjectRelation(project_data.id, _case.id, now, now)
                db.session.add(_case_relation) 
                               
                message = "add case success."
                db.session.flush()
                db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /manager?case_id=32342
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_query()                
        now = datetime.datetime.now()
        
        try: 
            case_data = _query.filter_by(id = param.get("case_id")).first()
                                    
            if not case_data:
                message = "do not have the case with case_id({})".format(param.get("case_id"))
                return jsonify(get_result("", status = False, message = message))
            
            for pp in ("name", "case_type"):
                _param = j_param.get(pp)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'Case parameter [{0}] should not be null.'.format(pp)))
                
                if pp == 'case_type':
                    if not _param.lower() in ('api', 'suite', 'case'):
                        return jsonify(get_result("", status = False, message = 'Case type should be in (api, suite, case).'))
                    
                    if _param == 'case' and j_param.get('func'):
                        return jsonify(get_result("", status = False, message = 'Invaild case with a function name.'))
                    
                    if (_param == 'api' or _param == 'suite') and not j_param.get('func'):
                        return jsonify(get_result("", status = False, message = 'Invaild api case or suite case. Do not have relation function.'))
                
            for i in ["name", "desc", "responsible", "tester", "case_type", "func"]:
                setattr(case_data, i, j_param.get(i,""))            
            case_data.update_time = now
                                    
            status = True
            message = "update case success."
            db.session.flush()
            db.session.commit()            
        except Exception as e:
            message = str(e)
            status = False
    
        return jsonify(get_result("", status = status, message = message))       
        
    
    def delete(self):
        # DELETE /manager?case_id=32342
        param = dict(request.args.items())
        _query = get_case_query()
        _query_relation = get_relation_query()
        _query_case_requests = get_case_requests_query()
        
        case_data = _query.filter_by(id = param.get("case_id")).first()
        
        if case_data:
            db.session.delete(case_data)
            
            # delete case_project_relation
            relation_datas = _query_relation.filter_by(case_id = param.get("case_id")).all()
            for relation_data in relation_datas:            
                db.session.delete(relation_data)
            
            # delete case_requests
            case_requests_datas = _query_case_requests.filter_by(case_id = param.get("case_id")).all()
            for case_requests_data in case_requests_datas:            
                db.session.delete(case_requests_data)
                
            db.session.commit()
            status = True
            message = "delete case success."        
        else:
            status = False
            message = "do not have the case with case_id({})".format(param.get("case_id"))
        return jsonify(get_result("", status = status,message = message))
    
    
if APP_ENV == "production":
    _case_view_manager = login_required(CaseView.as_view('case_view_manager'))    
else:
    _case_view_manager = CaseView.as_view('case_view_manager')      

case.add_url_rule('/manager', view_func=_case_view_manager)

