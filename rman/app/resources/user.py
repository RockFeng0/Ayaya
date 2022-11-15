#! python3
# -*- encoding: utf-8 -*-

from flask import current_app, jsonify, abort
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from rman.app import db
from rman.app.common import code
from rman.app.common.utils import pretty_result
from rman.app.models.user import UserModel


class UserListView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @login_required
    def get(self):
        """        GET /user?page=1&size=10
        获取分页任务记录的列表，支持参数筛选,参数如下：
            username  -- 用户名查询
            email   -- 邮箱查询
            identity -- 证件ID查询
        """

        _params = ('username', 'email', 'identity')
        self.parser.add_argument("page_num", type=int, location="args", default=1)
        self.parser.add_argument("page_size", type=int, location="args", default=10)
        _ = [self.parser.add_argument(i, type=str, location="args") for i in _params]
        args = self.parser.parse_args()

        try:
            _base_condition = {
                getattr(UserModel, i).like("%{0}%".format(args.get(i))) for i in _params if args.get(i)
            }

            all_conditions = {UserModel.is_delete == False}.union(_base_condition)
            base_condition = UserModel.query.filter(*all_conditions).order_by(UserModel.update_time.desc())
            pagination = base_condition.paginate(page=args.page_num, per_page=args.page_size, error_out=False)

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            items = [{
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "identity_id": user.identity_id,
                "role": user.role,
                "about_me": user.about_me,
                "last_seen": user.last_seen.strftime("%Y-%m-%d %H:%M:%S") if user.last_seen else None,
                "c_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": user.update_time.strftime("%Y-%m-%d %H:%M:%S")
            } for user in pagination.items]

            result = {
                'page_num': args.page_num,
                'page_size': args.page_size,
                "total": base_condition.count(),
                "records": items
            }
            return jsonify(pretty_result(code.OK, data=result))

    def post(self):
        """        POST /user
        用户注册，支持批量， 参数如下
            users  -- 添加任务，格式如：
                [{"username":'xxx', "email":'xxx',...}, {}, {}... ]
        """

        self.parser.add_argument("users", type=list, location="json", required=True)
        args = self.parser.parse_args()

        try:
            users = args.get("users")
            for user in users:
                if not isinstance(user, dict):
                    return jsonify(pretty_result(code.PARAM_ERROR))

            usernames = []
            emails = []
            identity_ids = []

            for _user in users:
                usernames.append(_user.get("username"))
                emails.append(_user.get("email"))
                identity_ids.append(str(_user.get("identity_id")))

            for item in usernames:
                if usernames.count(item) > 1:
                    return pretty_result(code.VALUE_ERROR, "重复的用户名'{0}'。".format(item))

                if UserModel.query.filter_by(username=item).first():
                    return pretty_result(code.VALUE_ERROR, "已注册的用户名'{0}'。".format(item))

            for item in emails:
                if emails.count(item) > 1:
                    return pretty_result(code.VALUE_ERROR, "重复的邮箱'{0}'。".format(item))

                if UserModel.query.filter_by(email=item).first():
                    return pretty_result(code.VALUE_ERROR, "已注册的邮箱'{0}'。".format(item))

            for item in identity_ids:
                if identity_ids.count(item) > 1:
                    return pretty_result(code.VALUE_ERROR, "重复的证件ID'{0}'。".format(item))

                if UserModel.query.filter_by(identity_id=item).first():
                    return pretty_result(code.VALUE_ERROR, "已注册的证件ID'{0}'。".format(item))

            for _user in users:
                user = UserModel()
                user.username = _user.get("username")
                user.email = _user.get("email")
                user.identity_id = str(_user.get("identity_id"))
                user.set_password(str(_user.get("password", "123456")))
                user.role = 0
                user.about_me = _user.get("about_me", "")
                db.session.add(user)
            db.session.flush()
            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))


class UserView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @staticmethod
    @login_required
    def get(uid):
        """        GET /user/1
        获取记录,参数如下：
            uid  -- 数据表的id
        """

        try:
            user = UserModel.query.get(uid)
            if not user or user.is_delete:
                abort(404)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            result = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "identity_id": user.identity_id,
                "role": user.role,
                "about_me": user.about_me,
                "last_seen": user.last_seen.strftime("%Y-%m-%d %H:%M:%S") if user.last_seen else None,
                "c_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": user.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return jsonify(pretty_result(code.OK, data=result))

    @login_required
    def put(self, uid):
        """       PUT /user/1
        更新记录,参数如下：
            uid  -- 数据表的id
        """
        self.parser.add_argument("email", type=str, location="json", required=True)
        self.parser.add_argument("role", type=str, location="json", required=True)
        self.parser.add_argument("about_me", type=str, location="json", required=True)
        args = self.parser.parse_args()

        try:
            user = UserModel.query.get(uid)
            if not user or user.is_delete:
                abort(404)
            user.email = args.email
            user.role = int(args.role)
            user.about_me = args.about_me

            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))

    @staticmethod
    @login_required
    def delete(uid):
        """       DELETE /user/1
        删除记录,参数如下：
            uid  -- 数据表的id
        """
        try:
            user = UserModel.query.get(uid)
            if not user or user.is_delete:
                abort(404)

            user.is_delete = True
            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return pretty_result(code.OK)
