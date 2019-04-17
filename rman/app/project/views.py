#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.project.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.project.views,  v1.0 2018年11月30日
    FROM:   2018年11月30日
********************************************************************
======================================================================

Provide a function for the automation test

'''
import datetime
from flask import request, jsonify
from flask_login import login_required
from flask.views import MethodView

from rman.app.project import project
from rman.app.project.models import Project, TestsetProjectRelation, db

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_query():
    return db.session.query(Project)

def get_relation_query():
    return db.session.query(TestsetProjectRelation)

@project.route("/get_distinct", methods=["GET"])
def distinct_col():
    # GET /project/get_distinct?col_name=module&name=xxxx
    param = dict(request.args.items())  
    _query = get_query()
    c_name = param.pop("col_name")    
    if not c_name in ("name", "module"):
        return jsonify(get_result("", status = False, message = "'col_name' should be in (name, module) for the Project table."))
    
    conditions = {i: param.get(i) for i in ('id', 'name', 'module') if param.get(i)}
    lines  = _query.filter_by(**conditions).with_entities(getattr(Project, c_name)).distinct().all()    
    
    result = [{"value": line[0]} for line in lines if line]
    return jsonify(get_result(result, message = "get all project {} success.".format(c_name)))
    
class ProjectView(MethodView):
    
    def get(self):
        # GET /manager?page=1&size=10
        param = dict(request.args.items())        
        _query = get_query()    
        
        conditions = {i: param.get(i) for i in ('id', 'name', 'module') if param.get(i)}        
        base_conditions = _query.filter_by(**conditions).order_by(Project.update_time.desc())
                
        page = int(param.get("page", 1))
        size = int(param.get("size", 10))        
        total = base_conditions.count()
        pagination = base_conditions.paginate(page = page, per_page= size, error_out=False)
        
        result = {"total": total, "projects":[]}
        result["projects"] = [{"id":pj.id,
                           "name": pj.name, 
                           "module":pj.module, 
                           "comment": pj.comment, 
                           "c_time": pj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                           "u_time": pj.update_time.strftime("%Y-%m-%d %H:%M:%S")
                           } for pj in pagination.items]
        
        return jsonify(get_result(result, message = "Query all data success in page: {0} size: {1}.".format(page, size)))
        
    
    def post(self):
        # POST /manager
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_query()  
        now = datetime.datetime.now() 
            
        try:
            for param in ("name", "module"):
                if not j_param.get(param):
                    return jsonify(get_result("", status = False, message = 'Parameter [{0}] should not be null.'.format(param)))
                    
            status = True
            project_data = _query.filter_by(name = j_param.get("name"), module = j_param.get("module")).first()
             
            if project_data:
                status = False
                message = "'{0}-{1}' already exists.".format(j_param.get("name"), j_param.get("module"))            
            else:
                project_data = Project(j_param.get("name"), j_param.get("module"), j_param.get("comment"),now,now)
                db.session.add(project_data)
                message = "add success."
                db.session.flush()
                db.session.commit()
        except Exception as e:
            message = str(e)
            status = False        
        #return redirect(url_for("project.search"))
        return jsonify(get_result("", status = status, message = message))
    
    def put(self):
        # PUT /?proj_id=32342
        param = dict(request.args.items())
        j_param = request.json if request.data else request.form.to_dict()
        _query = get_query()                
        now = datetime.datetime.now()
        
        try:
            project_data = _query.filter_by(id = param.get("proj_id")).first()
                                    
            if not project_data:
                message = "do not have the project with proj_id({})".format(param.get("proj_id"))
                return jsonify(get_result("", status = False, message = message))
                        
            _ = [setattr(project_data, i, j_param.get(i,"")) for i in ["name", "module", "comment"] if j_param.get(i)]                             
            project_data.update_time = now
            
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
        
        _query = get_query()
        _query_relation = get_relation_query() 
        
        try:
            proj_ids = param.get("ids").split(',')        
            result = {"delete_result":{}}
            for proj_id in proj_ids:
                project_data = _query.filter_by(id = proj_id).first()
                        
                if project_data:
                    db.session.delete(project_data)
                    
                    relation_datas = _query_relation.filter_by(project_id = proj_id).all()
                    
                    for relation_data in relation_datas:
                        db.session.delete(relation_data)
                                    
                    db.session.commit()
                    result["delete_result"][proj_id] = True                    
                else:
                    result["delete_result"][proj_id] = False
            
            status = False if False in result["delete_result"].values() else True        
            message = "delete done."
        except Exception as e:
            result = ''
            message = str(e)
            status = False
        
        return jsonify(get_result(result, status = status,message = message))


# _project_view_manager = login_required(ProjectView.as_view('project_view_manager'))
_project_view_manager = ProjectView.as_view('project_view_manager')
project.add_url_rule('/manager', view_func=_project_view_manager)
