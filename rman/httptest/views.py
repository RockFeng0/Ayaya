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

from rman.httptest import httptest
from rman.httptest.models import Case, CaseItemRequest, db
from rman.project.models import Project
from rman.project import project
from flask_login.utils import login_required

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_case_query():
    return Case.query

def get_case_item_request_query():
    return CaseItemRequest.query

def get_project_query():
    return Project.query

class CaseView(MethodView):
    
    def get(self):
        # GET /httptest?page=1&size=10
        
        param = dict(request.args.items())        
        _query = get_case_query()   
        _query_project = get_project_query() 
                        
        conditions = {i: param.get(i) for i in ('id', 'name', 'responsible', 'tester', 'case_type', 'project_id') if param.get(i)}
        base_conditions = _query.filter_by(**conditions).order_by(Case.update_time.desc())
            
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "cases":[]}
        for case in pagination.items:
            project = _query_project.filter_by(id = case.project_id).first()
            
            _case = {
                "id":case.id,
                "name": case.name, 
                "desc":case.desc, 
                "responsible": case.responsible,
                "tester": case.tester,
                "case_type": case.case_type,
                "func": case.func,
                "project_id": case.project_id,
                "project_name": project.name,
                
                "c_time": case.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": case.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            result["cases"].append(_case)
        
        return jsonify(get_result(result, message = "get all cases success in page: {0} size: {1}.".format(page, size)))
    
    def post(self):
        # POST /httptest        
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_query()
        _query_project = get_project_query()       
        now = datetime.datetime.now()
        
        try:
            
            for param in ("name", "case_type", "project_name"):
                _param = j_param.get(param)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'Case parameter {0} should not be null.'.format(param)))
                
                if param == 'case_type':
                    if not _param.lower() in ('api', 'suite', 'case'):
                        return jsonify(get_result("", status = False, message = 'Case type should be in (api, suite, case).'))
                    
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
                     project_data.id, now, now)
                
                db.session.add(_case)
                message = "add case success."
                db.session.flush()
                db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /httptest?case_id=32342
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_case_query()
        _query_project = get_project_query()       
        now = datetime.datetime.now()
        
        try: 
            case_data = _query.filter_by(id = param.get("case_id")).first()
            project_data = _query_project.filter_by(name = j_param.get("project_name")).first()
            
            if not project_data:
                message = "Unknow project named '{0}'.".format(j_param.get("project_name"))
                return jsonify(get_result("", status = False, message = message))
            
            if not case_data:
                message = "do not have the case with case_id({})".format(param.get("case_id"))
                return jsonify(get_result("", status = False, message = message))
            
            for pp in ("name", "case_type", "project_name"):
                _param = j_param.get(pp)
                if not _param:
                    return jsonify(get_result("", status = False, message = 'Case parameter {0} should not be null.'.format(pp)))
                
                if pp == 'case_type':
                    if not _param.lower() in ('api', 'suite', 'case'):
                        return jsonify(get_result("", status = False, message = 'Case type should be in (api, suite, case).'))
                    
                    if (_param == 'api' or _param == 'suite') and not j_param.get('func'):
                        return jsonify(get_result("", status = False, message = 'Invaild api case or suite case. Do not have relation function.'))
                
            for i in ["name", "desc", "responsible", "tester", "case_type", "func"]:
                setattr(case_data, i, j_param.get(i,""))
            
            case_data.project_id = project_data.id
            case_data.update_time = now               
            
            status = True
            message = "update project success."
            db.session.flush()
            db.session.commit()
        except Exception as e:
            message = str(e)
            status = False
    
        return jsonify(get_result("", status = status, message = message))       
        
    
    def delete(self):
        # DELETE /httptest?case_id=32342
        param = dict(request.args.items())
        _query = get_case_query()
        case_data = _query.filter_by(id = param.get("case_id")).first()
        
        if case_data:
            db.session.delete(case_data)
            db.session.commit()
            status = True
            message = "delete case success."        
        else:
            status = False
            message = "do not have the case with case_id({})".format(param.get("case_id"))
        return jsonify(get_result("", status = status,message = message))
    
@httptest.route('/test', methods= ['GET'])
def test():
    return 'good'
    
_case_view_manager = login_required(CaseView.as_view('case_view_manager'))
# _case_view_manager = CaseView.as_view('case_view_manager')
httptest.add_url_rule('/manager', view_func=_case_view_manager)

    