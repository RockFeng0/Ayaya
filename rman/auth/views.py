#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.auth.views

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.auth.views,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''
import datetime
from . import auth
from .models import User, db
from rman import login_manager
from flask import request,jsonify
from flask_login import login_user, logout_user, current_user

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_query():
    return User.query

@login_manager.user_loader
def load_user(userid):
    _query = get_query()
    return _query.filter_by(id = userid).first()


def is_user_exists(username, email, identity_id):
    _query = get_query()
    if username:
        user = _query.filter_by(username = username).first()
    elif email:
        user = _query.filter_by(username = email).first()
    elif identity_id:
        user = _query.filter_by(username = identity_id).first()
    else:
        return False
    return True if user else False

@auth.route("/login", methods = ["POST"])
def login():
    # POST /login
    j_param = request.json if request.data else {}
    _query = get_query()
    
    try:  
        
        if j_param.get("username"):
            user = _query.filter_by(username = j_param.get("username")).first()
        elif j_param.get("email"):
            user = _query.filter_by(username = j_param.get("email")).first()
        elif j_param.get("identity_id"):
            user = _query.filter_by(username = j_param.get("identity_id")).first()
        else:
            return jsonify(get_result("", status = False, message = 'Need username or email or identity_id'))
        
        if not user:
            return jsonify(get_result("", status = False, message = 'Not a registered user.'))
        
        password = str(j_param.get("password"))
        if not password:
            return jsonify(get_result("", status = False, message = 'Need password.'))
        
        if user.check_password(password):
            login_user(user)
            return jsonify(get_result("", status = True, message = 'Login success.'))
        else:
            return jsonify(get_result("", status = False, message = 'Password not correct.'))
            
    except Exception as e:
        message = str(e) 
        return jsonify(get_result("", status = False, message = 'Error: {}'.format(message)))
    
@auth.route("/register", methods = ["POST"])
def register():
    # POST /register
    j_param = request.json
    _query = get_query()
    
    try:  
        username    = j_param.get("username")
        email       = j_param.get("email")
        identity_id = j_param.get("identity_id")
        password    = str(j_param.get("password","")) 
        role        = 0
        about_me    = j_param.get("about_me")
        now         = datetime.datetime.now()
        
        
        if username:
            user = _query.filter_by(username = username).first()
        elif email:
            user = _query.filter_by(username = email).first()
        elif identity_id:
            user = _query.filter_by(username = identity_id).first()
            
        if user:
            return jsonify(get_result("", status = False, message = "User already exists, can't register."))        
        
        user = User(username, email, password, identity_id, role, about_me, now)
        user.set_password(user.password)
        
        status = True
        db.session.add(user)        
        message = "Register user success."
        db.session.flush()
        db.session.commit()
        
    except Exception as e:
        status = False
        message = 'Error: {}'.format(str(e))   
    return jsonify(get_result("", status = status, message = message))

@auth.route("/update_user", methods = ["PUT"])
def update_user():    
    # PUT 
    # /update_user?user_id=32342&type=info
    # /update_user?user_id=32342&type=password
    # /update_user?user_id=32342&type=identity
    now = datetime.datetime.now()
    param = dict(request.args.items())
    j_param = request.json
    _query = get_query()
        
    user = _query.filter_by(id = param.get("user_id")).first()
    utype = param.get("type")
    
    if user:
        status = True
        
        if utype == "info":
            for i in ["username", "email", "about_me"]:
                setattr(user, i, j_param.get(i,""))
            user.update_time = now           
            message = "update user info success."
            
        elif utype == "password":        
            user.set_password(j_param.get("password",""))
            message = "update user password success."
        
        elif utype == "identity":
            user.identity_id = j_param.get("identity_id","")
            message = "update user identity_id success."
        
        db.session.flush()
        db.session.commit()
    else:
        status = False
        message = "do not have the project with user_id({})".format(param.get("user_id"))
        
    return jsonify(get_result("", status = status,message = message))

@auth.route("/logout", methods = ["GET"])
def logout():
    # GET /logout
    try:
        status = logout_user()
        message = "Logout success."
    except Exception as e:
        status = False
        message = 'Error: {}'.format(str(e))   
    return jsonify(get_result("", status = status, message = message))
