#! python3
# -*- encoding: utf-8 -*-

import datetime
from rman.app import db, bcrypt
from .base import BaseModel

from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeSerializer

ROLE_USER = 0
ROLE_ADMIN = 1


class UserModel(db.Model, BaseModel, UserMixin):
    """
    用户表
    """
    # __bind_key__ = 'auto'
    __tablename__ = "user"

    username = db.Column(db.String(24), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(24), unique=True, nullable=False, comment='邮箱')
    identity_id = db.Column(db.String(18), unique=True, nullable=False, comment='证件ID')
    password = db.Column(db.String(), nullable=False, comment='密码')
    role = db.Column(db.SmallInteger, default=ROLE_USER, comment='角色')
    about_me = db.Column(db.String(140), comment='描述')
    last_seen = db.Column(db.DateTime, comment='上次登录时间')

    def get_id(self, life_time=None):
        """获取token值"""
        key = current_app.config.get("SECRET_KEY", "It's a secret.")
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
        return '<User %r>' % self.username
