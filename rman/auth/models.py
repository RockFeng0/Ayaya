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

from rman import db
from sqlalchemy import Column, Integer, String, SmallInteger, DateTime
from flask_login import UserMixin
from rman import bcrypt

ROLE_USER = 0
ROLE_ADMIN = 1
 
class User(db.Model, UserMixin):
    ''' 用户   '''
    __tablename__ = "user"
    
    id          = Column(Integer, primary_key = True)
    name        = Column(String(24), unique = True, nullable = False)
    email       = Column(String(24), unique = True, nullable = False)
    identity_id = Column(String(18), unique = True, nullable = False)
    password    = Column(String(), nullable = False)
    role        = Column(SmallInteger, default = ROLE_USER)
    about_me    = Column(String(140))
    last_seen   = Column(DateTime)
    
    def __init__(self, name, email, passwd, identity_id, role, about_me, last_seen):
        self.name   = name
        self.email  = email
        self.password = passwd
        self.identity_id = identity_id
        self.role   = role
        self.about_me = about_me
        self.last_seen = last_seen
    
    def set_password(self):
        self.password = bcrypt.generate_password_hash(self.password)
 
    def check_password(self, passwd):
        return bcrypt.check_password_hash(self.password, passwd)
    
    def __repr__(self):
        return '<User %r>' % (self.name)
