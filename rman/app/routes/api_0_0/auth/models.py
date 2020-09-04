#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.auth.models

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.auth.models,  v1.0 2018年11月22日
    FROM:   2018年11月22日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman.app import db, bcrypt
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeSerializer

ROLE_USER = 0
ROLE_ADMIN = 1
 
class User(db.Model, UserMixin):
    ''' 用户   '''
    __tablename__ = "user"
    
    id          = Column(Integer, primary_key = True)
    username    = Column(String(24), unique = True, nullable = False)
    email       = Column(String(24), unique = True, nullable = False)
    identity_id = Column(String(18), unique = True, nullable = False)
    password    = Column(String(), nullable = False)
    role        = Column(SmallInteger, default = ROLE_USER)
    about_me    = Column(String(140))
    last_seen   = Column(DateTime)
    
    def __init__(self, name, email, passwd, identity_id, role, about_me, last_seen):
        self.username   = name
        self.email  = email        
        self.set_password(passwd)
        self.identity_id = identity_id
        self.role   = role
        self.about_me = about_me
        self.last_seen = last_seen
    
    def get_id(self, life_time=None):        
        key = current_app.config.get("SECRET_KEY","It's a secret.")
        s = URLSafeSerializer(key)
        if not life_time:
            life_time = current_app.config.get("TOKEN_LIFETIME")        
        token = s.dumps((self.id, self.username, str(self.password), life_time))        
        return token

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)        
 
    def check_password(self, passwd):
        return bcrypt.check_password_hash(self.password, passwd)    
    
    def __repr__(self):
        return '<User %r>' % (self.username)
