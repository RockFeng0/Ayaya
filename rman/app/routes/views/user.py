#! python3
# -*- encoding: utf-8 -*-


from flask import Blueprint
from flask_restful import Api
from rman.app.resources import user as res_user

user = Blueprint('user', __name__)

api = Api(user)
api.add_resource(res_user.UserListView, '/user')
api.add_resource(res_user.UserView, '/user/<int:uid>')
