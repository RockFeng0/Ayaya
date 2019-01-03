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
from rman import login_manager,simple_cache
from rman.auth import auth
from rman.auth.models import User, db

import datetime
from itsdangerous import URLSafeSerializer, BadData
from flask import request,jsonify, current_app
from flask_login import login_user, logout_user, login_required

def get_result(result, status=True, message="success" ):
    return {"status":status, "message":message,"result":result}

def get_query():
    return User.query


@login_manager.user_loader
def load_user(token):
    _query = get_query()
#     return _query.filter_by(id = userid).first()
    key = current_app.config.get("SECRET_KEY", "It's a secret.")
    try:
        s = URLSafeSerializer(key)
        userid, username, password, life_time = s.loads(token)
    except BadData:
        # token had been modified!
        return None
  
    # 校验密码
    user = _query.get(userid)
    if user:
        # 能loads出id，name等信息，说明已经成功登录过，那么cache中就应该有token的缓存
        token_cache = simple_cache.get(token)
        if not token_cache:  # 此处找不到有2个原因：1.cache中因为超时失效（属于正常情况）；2.cache机制出错（属于异常情况）。
            # the token is not found in cache.
            return None
        
        if str(password) != str(user.password):            
            # the password in token is not matched!            
            simple_cache.delete(token)
            return None
        else:
            simple_cache.set(token, 1, timeout=life_time)
    else:
        # the user is not found, the token is invalid!
        return None
    return user
    

@auth.route("/login", methods = ["POST"])
def login():
    # POST /login
    j_param = request.json if request.data else {}
    _query = get_query()
    
    try:    
        if j_param.get("username"):
            user = _query.filter_by(username = j_param.get("username")).first()
        elif j_param.get("email"):
            user = _query.filter_by(email = j_param.get("email")).first()
        elif j_param.get("identity_id"):
            user = _query.filter_by(identity_id = j_param.get("identity_id")).first()
        else:
            return jsonify(get_result("", status = False, message = 'Need username or email or identity_id'))
        
        if not user:
            return jsonify(get_result("", status = False, message = 'Not a registered user.'))
        
        password = str(j_param.get("password"))        
        if not password:
            return jsonify(get_result("", status = False, message = 'Need password.'))
        
        if user.check_password(password):
            remember_me = True if j_param.get("remember") else False            
            login_user(user, remember=remember_me)
            
            life_time = current_app.config.get("TOKEN_LIFETIME")
            token = user.get_id(life_time)            
            simple_cache.set(token, 1, life_time)
                         
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
            user = _query.filter_by(email = email).first()
        elif identity_id:
            user = _query.filter_by(identity_id = identity_id).first()
            
        if user:
            return jsonify(get_result("", status = False, message = "User already exists, can't register."))        
        
        user = User(username, email, password, identity_id, role, about_me, now)
                
        db.session.add(user)        
        db.session.flush()
        db.session.commit()
        status = True        
        message = "Register user success."
                
    except Exception as e:
        status = False
        message = 'Error: {}'.format(str(e))   
    return jsonify(get_result("", status = status, message = message))

@auth.route("/update_user", methods = ["PUT"])
@login_required
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
@login_required
def logout():
    # GET /logout
    try:           
        status = logout_user()
        message = "Logout success."        
    except Exception as e:
        status = False
        message = 'Error: {}'.format(str(e))   
    return jsonify(get_result("", status = status, message = message))

@auth.route('/test', methods = ['GET'])
@login_required
def test():
    return "sdfsdf"
