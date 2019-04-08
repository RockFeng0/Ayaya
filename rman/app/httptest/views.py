#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.httptest.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.httptest.views,  v1.0 2018年11月21日
    FROM:   2018年11月21日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import datetime
from flask import request, jsonify
from flask_login import login_required
from flask.views import MethodView

from rman.app import APP_ENV
from rman.app.httptest import httptest
from rman.app.httptest.models import Case, CaseRequests, CaseRecord, db
from rman.app.project.models import Project, CaseProjectRelation

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_project_query():
    return db.session.query(Project)

def get_case_query():
    return db.session.query(Case)

def get_relation_query():
    return db.session.query(CaseProjectRelation)

def get_case_requests_query():
    return db.session.query(CaseRequests)

def get_case_join_project_query():    
    return db.session.query(Case, Project.name)\
        .join(CaseProjectRelation,Case.id == CaseProjectRelation.case_id)\
        .join(Project, CaseProjectRelation.project_id == Project.id)
        
def get_requests_join_case_query():
    return db.session.query(CaseRequests).join(Case, CaseRequests.case_id == Case.id)    

class CaseView(MethodView):
    
    def get(self):
        # GET /case?page=1&size=10        
        param = dict(request.args.items())        
#         _query = get_case_query()   
#         _query_project = get_project_query() 
        _query_case_join_project = get_case_join_project_query()
                     
        conditions = {i: param.get(i) for i in ('id', 'name', 'responsible', 'tester', 'case_type') if param.get(i)}
        base_conditions = _query_case_join_project.filter_by(**conditions).order_by(Case.update_time.desc())
        print(base_conditions)
                
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "cases":[]}
        print(pagination.items)
        for case in pagination.items:
#             project = _query_project.filter_by(id = case.project_id).first()
            
            _case = {
#                 "id":case.id,
                "name": case.name, 
                "desc":case.desc, 
                "responsible": case.responsible,
                "tester": case.tester,
                "case_type": case.case_type,
                "func": case.func,
#                 "project_id": case.project_id,
                "project_name": case.project_name,
                
                "c_time": case.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": case.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["cases"].append(_case)
        
        return jsonify(get_result(result, message = "get all cases success in page: {0} size: {1}.".format(page, size)))
    
    def post(self):
        # POST /case        
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_query()
        _query_project = get_project_query()       
        now = datetime.datetime.now()
        
        try:
            
            for param in ("name", "case_type", "project_name"):
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
            project_data = _query_project.filter_by(name = j_param.get("project_name")).first()
            
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
        # PUT /case?case_id=32342
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
        # DELETE /case?case_id=32342
        param = dict(request.args.items())
        _query = get_case_query()
        _query_relation = get_relation_query()
        _query_case_requests = get_case_requests_query()
        
        case_data = _query.filter_by(id = param.get("case_id")).first()
        
        if case_data:
            db.session.delete(case_data)
            
            relation_datas = _query_relation.filter_by(case_id = param.get("case_id")).all()
            for relation_data in relation_datas:            
                db.session.delete(relation_data)
                
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

class CaseRequestsView(MethodView):
    
    def get(self):
        # GET /case_requests?page=1&size=10
        
        param = dict(request.args.items())
        _query_requests_join_case = get_requests_join_case_query()
                     
        conditions = {getattr(Case,i): param.get(i) for i in ('id', 'name', 'responsible', 'tester', 'case_type') if param.get(i)}        
        base_conditions = _query_requests_join_case.filter_by(**conditions).order_by(Case.update_time.desc())
                
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "cases":[]}
        for case in pagination.items:
           
            _case = {
                "id":case.id,
                "name": case.name, 
                "desc":case.desc, 
                "responsible": case.responsible,
                "tester": case.tester,
                "case_type": case.case_type,
                "func": case.func,
                
                "glob_var": case.glob_var,
                "glob_regx": case.glob_regx,                
                "pre_command":case.pre_command,
                "url":case.url,
                "method":case.method,
                "hearders":case.hearders,
                "body":case.body,
                "post_command":case.post_command,
                "verify":case.verify,
                
                
                "c_time": case.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": case.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["cases"].append(_case)
        
        return jsonify(get_result(result, message = "get all cases_requests success in page: {0} size: {1}.".format(page, size)))
    
    
    def post(self):
        # POST /case_requests        
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_requests_query()
        _query_case = get_case_query()       
        now = datetime.datetime.now()
        
        try:
            
            for param in ("url", "method", "case_name"):
                _param = j_param.get(param)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'CaseRequests parameter [{0}] should not be null.'.format(param)))
                                                    
            status = True
            case_data = _query_case.filter_by(name = j_param.get("case_name")).first()
            
            if not case_data:
                status = False
                message = "Do not have this case named '{0}'.".format(j_param.get("case_data"))
                            
            else:
                _case_requests = CaseRequests(j_param.get("glob_var", {}),
                     j_param.get("glob_regx",{}), 
                     j_param.get("pre_command",[]),
                     j_param.get("url"),
                     j_param.get("method"),
                     j_param.get("hearders", {}),
                     j_param.get("body", {}),
                     j_param.get("post_command",[]),
                     j_param.get("verify",[]),
                     case_data.id,now, now)                
                db.session.add(_case_requests)
                db.session.commit()
                                               
                message = "add case_requests success."
                db.session.flush()
                db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /case_requests?case_requests_id=32342
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_requests_query()                
        now = datetime.datetime.now()
        
        try: 
            case_requests_data = _query.filter_by(id = param.get("case_requests_id")).first()
                                    
            if not case_requests_data:
                message = "do not have the case_requests with case_requests_id({})".format(param.get("case_requests_id"))
                return jsonify(get_result("", status = False, message = message))
            
            for pp in ("url", "method"):
                _param = j_param.get(pp)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'CaseRequests parameter [{0}] should not be null.'.format(pp)))
                
            
            for i in ["glob_var", "glob_regx", "hearders", "body"]:
                setattr(case_requests_data, i, j_param.get(i,{}))
            
            for i in ["pre_command", "post_command", "verify"]:
                setattr(case_requests_data, i, j_param.get(i,[]))
                
            case_requests_data.url = j_param.get("url")
            case_requests_data.method = j_param.get("method")
            case_requests_data.update_time = now
                                    
            status = True
            message = "update case_requests success."
            db.session.flush()
            db.session.commit()            
        except Exception as e:
            message = str(e)
            status = False
    
        return jsonify(get_result("", status = status, message = message))       
    
    def delete(self):
        # DELETE /case_requests?case_requests_id=32342
        param = dict(request.args.items())
        _query = get_case_requests_query()        
        case_requests_data = _query.filter_by(id = param.get("case_requests_id")).first()
        
        if case_requests_data:
            db.session.delete(case_requests_data)                            
            db.session.commit()
            status = True
            message = "delete case_requests success."        
        else:
            status = False
            message = "do not have the case_requests with case_requests_id({})".format(param.get("case_requests_id"))
        return jsonify(get_result("", status = status,message = message))


class CaseRecordView(MethodView):
    
    def get(self):
        pass
    
    def post(self):
        pass
    
    def put(self):
        pass

    
@httptest.route('/test', methods= ['GET'])
def test():
    return 'good'

if APP_ENV == "production":
    _case_view_manager = login_required(CaseView.as_view('case_view_manager'))
    _case_requests_view_manager = login_required(CaseRequestsView.as_view('case_requests_view_manager'))
else:
    _case_view_manager = CaseView.as_view('case_view_manager')
    _case_requests_view_manager = CaseRequestsView.as_view('case_requests_view_manager')  

httptest.add_url_rule('/case', view_func=_case_view_manager)
httptest.add_url_rule('/case_requests', view_func=_case_requests_view_manager)
    