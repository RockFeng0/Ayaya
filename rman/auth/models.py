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

ROLE_USER = 0
ROLE_ADMIN = 1
 
class User(db.Model):
    ''' 用户   '''
    __tablename__ = "user"
    
    id          = Column(Integer, primary_key = True)
    name        = Column(String(24), unique = True)
    email       = Column(String(24), unique = True)
    password    = Column(String(16))
    identity_id = Column(String(16))
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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
    
    def __repr__(self):
        return '<User %r>' % (self.name)