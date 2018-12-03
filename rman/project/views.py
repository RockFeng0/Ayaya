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
from flask import make_response, request, redirect, url_for, render_template
import datetime

class ProjectForm(Form):
    name = TextField('项目名称:', [validators.length(1, 32, "项目名称最多32字符")])
    module = TextField('待测模块:', [validators.length(1, 32, "待测模块最多32字符")])
    comment = TextField('备注:', [validators.length(1, 128, "备注最多128字符")])
    submit = SubmitField('提交')
    
    
@project.route('/search')
def search():    
    all_obj = Project.query.order_by(Project.update_time.desc()).all()    
    result = [{"name": pj.name, "module":pj.module, "comment": pj.comment} for pj in all_obj]    
    return make_response(render_template("project/project.html", projects = result))
    
@project.route("/update", methods = ["GET","POST"])
def update():    
    form = ProjectForm(request.form)
    now = datetime.datetime.now()
    
    if request.method == "GET":
        return make_response(render_template("project/project.html", form = form))
    
    elif request.method == "POST" and form.validate():        
        project_data = Project.query.filter_by(name = form.name.data, module = form.module.data).first()
        
        if project_data:
            project_data.update_time = now
        else:
            project_data = Project(form.name.data, form.module.data, form.comment.data,now,now)
            db.session.add(project_data)
        db.session.flush()
        db.session.commit()
        return redirect(url_for("project.search"))

@project.route("/delete", methods = ["POST"])
def delete():
    pass
