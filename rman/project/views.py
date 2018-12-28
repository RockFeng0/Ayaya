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

from rman.project import project
from rman.project.models import Project, db

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_query():
    return Project.query

@project.route("/manager", methods = ["GET","POST","DELETE","PUT"])
@login_required
def manage_project():
    param = dict(request.args.items())
    j_param = request.json if request.data else {}
    _query = get_query()    
    now = datetime.datetime.now()
    
    has_proj_id = True if param.get("proj_id") else False
    pj = _query.filter_by(id = param.get("proj_id")).first()
    if request.method == "GET":        
        
        # GET /manager
        if not has_proj_id:            
            all_obj = _query.order_by(Project.update_time.desc()).all()    
            result = [{"id":pj.id,
                       "name": pj.name, 
                       "module":pj.module, 
                       "comment": pj.comment, 
                       "c_time": pj.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                       "u_time": pj.update_time.strftime("%Y-%m-%d %H:%M:%S")
                       } for pj in all_obj]
            return jsonify(get_result(result, message = "get all project success."))
        
        # GET /manager?proj_id=32342
        if pj:            
            status = True
            result = {"id":pj.id,"name": pj.name, "module":pj.module, "comment": pj.comment}
            message = "get project success."
        else:
            status = False
            result = ""
            message = "do not have the project with proj_id({})".format(param.get("proj_id"))
        return jsonify(get_result(result, status = status,message = message))
    
    elif request.method == "POST":   
        # POST /manager    
        try:            
            status = True
            project_data = _query.filter_by(name = j_param.get("name"), module = j_param.get("module")).first()
             
            if project_data:
                status = False
                message = "this project is already exists."                
            else:
                project_data = Project(j_param.get("name"), j_param.get("module"), j_param.get("comment"),now,now)
                db.session.add(project_data)
                message = "add project success."
                db.session.flush()
                db.session.commit()
        except Exception as e:
            message = str(e)
            status = False        
        #return redirect(url_for("project.search"))
        return jsonify(get_result("", status = status, message = message))
    
    elif request.method == "DELETE":
        # DELETE /manager?proj_id=32342
        if pj:
            db.session.delete(pj)
            db.session.commit()
            status = True
            message = "delete project success."        
        else:
            status = False
            message = "do not have the project with proj_id({})".format(param.get("proj_id"))
        return jsonify(get_result("", status = status,message = message))
    
    elif request.method == "PUT":
        # PUT /?proj_id=32342
        if pj:
            for i in ["name", "module", "comment"]:
                setattr(pj, i, j_param.get(i,""))
            pj.update_time = now
            status = True
            message = "update project success."
            db.session.flush()
            db.session.commit()
        else:
            status = False
            message = "do not have the project with proj_id({})".format(param.get("proj_id"))
        return jsonify(get_result("", status = status,message = message))
    



