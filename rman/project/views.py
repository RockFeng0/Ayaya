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

from . import project
from .models import Project, db
from flask_wtf import Form 
from wtforms import TextField, SubmitField, validators
from flask import make_response, request, redirect, url_for, render_template, jsonify
import datetime

class ProjectForm(Form):
    name = TextField('项目名称:', [validators.length(1, 32, "项目名称最多32字符")])
    module = TextField('待测模块:', [validators.length(1, 32, "待测模块最多32字符")])
    comment = TextField('备注:', [validators.length(1, 128, "备注最多128字符")])
    submit = SubmitField('提交')
    
def get_query():
    return Project.query
    
def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}
    
@project.route('/search')
def search():
    _query = get_query()  
    all_obj = _query.order_by(Project.update_time.desc()).all()    
    result = [{"id":pj.id,"name": pj.name, "module":pj.module, "comment": pj.comment} for pj in all_obj]    
    return make_response(render_template("project/project.html", projects = get_result(result, message = "search success.")))
    #return jsonify(msg)
    
@project.route("/update", methods = ["GET","POST"])
def update():    
    form = ProjectForm(request.form)
    now = datetime.datetime.now()
     
    if request.method == "GET":
        return make_response(render_template("project/project.html", form = form))
     
    elif request.method == "POST" and form.validate():
        _query = get_query()    
        project_data = _query.filter_by(name = form.name.data, module = form.module.data).first()
         
        if project_data:
            project_data.update_time = now
        else:
            project_data = Project(form.name.data, form.module.data, form.comment.data,now,now)
            db.session.add(project_data)
        db.session.flush()
        db.session.commit()
        return redirect(url_for("project.search"))
 
@project.route("/detail", methods=["GET"])
def detail():
    param = dict(request.args.items())
    _query = get_query()
    pj = _query.filter_by(id = param.get("proj_id")).first()
    if pj:
        status = True
        result = {"id":pj.id,"name": pj.name, "module":pj.module, "comment": pj.comment}
        message = "detail success."
    else:
        status = False
        result = ""
        message = "do not have the project with proj_id({})".format(param.get("proj_id"))
    return jsonify(get_result(result, status = status,message = message))
 
@project.route("/delete", methods = ["GET"])
def delete():    
    param = dict(request.args.items())    
    _query = get_query()
    pj = _query.filter_by(id = param.get("proj_id")).first()
    result = ""
    if pj:
        db.session.delete(pj)
        db.session.commit()
        status = True
        message = "delete success."        
    else:
        status = False
        message = "do not have the project with proj_id({})".format(param.get("proj_id"))
    return jsonify(get_result(result, status = status,message = message))


