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
from rman.app.models.m_project import ProjectModel


class ProjectListView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @login_required
    def get(self):
        """        GET /project?page=1&size=10
        获取分页任务记录的列表，支持参数筛选,参数如下：
            name  -- 项目名称
        """

        _params = ('name',)
        self.parser.add_argument("page_num", type=int, location="args", default=1)
        self.parser.add_argument("page_size", type=int, location="args", default=10)
        _ = [self.parser.add_argument(i, type=str, location="args") for i in _params]
        args = self.parser.parse_args()

        try:
            _base_condition = {
                getattr(ProjectModel, i).like("%{0}%".format(args.get(i))) for i in _params if args.get(i)
            }

            all_conditions = {ProjectModel.is_delete == False}.union(_base_condition)
            base_condition = ProjectModel.query.filter(*all_conditions).order_by(ProjectModel.update_time.desc())
            pagination = base_condition.paginate(page=args.page_num, per_page=args.page_size, error_out=False)

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            items = [{
                "id": item.id,
                "name": item.name,
                "comment": item.comment,
                "department_id": item.department_id,
                "c_time": item.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": item.update_time.strftime("%Y-%m-%d %H:%M:%S")
            } for item in pagination.items]

            result = {
                'page_num': args.page_num,
                'page_size': args.page_size,
                "total": base_condition.count(),
                "records": items
            }
            return jsonify(pretty_result(code.OK, data=result))

    def post(self):
        """        POST /project
        记录新增，支持批量， 参数如下
            users  -- 添加任务，格式如：
                [{"name":'xxx', "comment":'xxx',...}, {}, {}... ]
        """

        self.parser.add_argument("items", type=list, location="json", required=True)
        args = self.parser.parse_args()

        try:
            items = args.get("items")
            for item in items:
                if not isinstance(item, dict):
                    return jsonify(pretty_result(code.PARAM_ERROR))

            for _item in items:
                project = ProjectModel()
                project.name = _item.get("name")
                project.comment = _item.get("comment")
                project.department_id = int(_item.get("department_id"))
                db.session.add(project)
            db.session.flush()
            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))


class ProjectView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @staticmethod
    @login_required
    def get(uid):
        """        GET /project/1
        获取记录,参数如下：
            uid  -- 数据表的id
        """

        try:
            item = ProjectModel.query.get(uid)
            if not item or item.is_delete:
                abort(404)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            result = {
                "id": item.id,
                "name": item.name,
                "comment": item.comment,
                "department_id": item.department_id,
                "c_time": item.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": item.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return jsonify(pretty_result(code.OK, data=result))

    @login_required
    def put(self, uid):
        """       PUT /project/1
        更新记录,参数如下：
            uid  -- 数据表的id
        """

        self.parser.add_argument("name", type=str, location="json", required=True)
        self.parser.add_argument("comment", type=str, location="json", required=False)
        self.parser.add_argument("department_id", type=int, location="json", required=False)
        args = self.parser.parse_args()

        try:
            item = ProjectModel.query.get(uid)
            if not item or item.is_delete:
                abort(404)

            item.name = args.name
            item.comment = args.comment
            item.department_id = int(args.department_id)

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
        """       DELETE /project/1
        删除记录,参数如下：
            uid  -- 数据表的id
        """
        try:
            item = ProjectModel.query.get(uid)
            if not item or item.is_delete:
                abort(404)

            item.is_delete = True
            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return pretty_result(code.OK)

