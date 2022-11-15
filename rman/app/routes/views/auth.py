#! python3
# -*- encoding: utf-8 -*-

import datetime
from itsdangerous import URLSafeSerializer, BadData
from flask import Blueprint
from flask import request, jsonify, current_app
from flask_login import login_user, logout_user, login_required

from rman.app import login_manager, simple_cache, db
from rman.app.models.user import UserModel
from rman.app.common import code
from rman.app.common.utils import pretty_result

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(token):
    key = current_app.config.get("SECRET_KEY", "It's a secret.")
    try:
        s = URLSafeSerializer(key)
        userid, username, password, life_time = s.loads(token)
    except BadData:
        # token had been modified!
        return None

    # 校验密码
    user = db.session.query(UserModel).get(userid)
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


@auth.route("/auth/login", methods=["POST"])
def login():
    # POST /login
    j_param = request.json if request.data else request.form.to_dict()

    try:
        user = db.session.query(UserModel).filter(
            db.or_(
                UserModel.username == j_param.get("username"),
                UserModel.email == j_param.get("email"),
                UserModel.identity_id == j_param.get("identity_id"),
            )
        ).first()

        if not user or user.is_delete:
            return pretty_result(code.VALUE_ERROR, '未注册的用户，请先注册。')

        password = str(j_param.get("password"))
        if not password:
            return pretty_result(code.VALUE_ERROR, '请填写密码。')

        if user.check_password(password):
            remember_me = True if j_param.get("remember") else False
            login_user(user, remember=remember_me)

            life_time = current_app.config.get("TOKEN_LIFETIME")
            token = user.get_id(life_time)
            simple_cache.set(token, 1, life_time)

            user.last_seen = datetime.datetime.now()
            db.session.flush()
            db.session.commit()
            return pretty_result(code.OK, data={"token": token, "username": user.username})
        else:
            return pretty_result(code.AUTHORIZATION_ERROR, '用户名或密码错误。')

    except Exception as e:
        message = str(e)
        return pretty_result(code.UNKNOWN_ERROR, 'Error: {}'.format(message))


@auth.route("/auth/logout", methods=["GET"])
@login_required
def logout():
    # GET /logout
    status = code.OK
    try:
        logout_user()
        message = "Logout success."
    except Exception as e:
        status = code.UNKNOWN_ERROR
        message = 'Error: {}'.format(str(e))
    return pretty_result(status, message)


@auth.route('/test', methods=['GET'])
@login_required
def test():
    return "sdfsdf"
