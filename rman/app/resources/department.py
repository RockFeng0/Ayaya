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
from rman.app.models.m_department import DepartmentModel


class DepartmentListView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @login_required
    def get(self):
        """        GET /department?page=1&size=10
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
                getattr(DepartmentModel, i).like("%{0}%".format(args.get(i))) for i in _params if args.get(i)
            }

            all_conditions = {DepartmentModel.is_delete == False}.union(_base_condition)
            base_condition = DepartmentModel.query.filter(*all_conditions).order_by(DepartmentModel.update_time.desc())
            pagination = base_condition.paginate(page=args.page_num, per_page=args.page_size, error_out=False)

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            items = [{
                "id": item.id,
                "name": item.name,
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

    @login_required
    def post(self):
        """        POST /department
        记录新增，支持批量， 参数如下
            items  -- 添加任务，格式如：
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
                if db.session.query(DepartmentModel).filter_by(name=_item.get("name")).first():
                    continue
                item = DepartmentModel()
                item.name = _item.get("name")
                db.session.add(item)
            db.session.flush()
            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))


class DepartmentView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @staticmethod
    @login_required
    def get(uid):
        """        GET /department/1
        获取记录,参数如下：
            uid  -- 数据表的id
        """

        try:
            item = DepartmentModel.query.get(uid)
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
                "c_time": item.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": item.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return jsonify(pretty_result(code.OK, data=result))

    @login_required
    def put(self, uid):
        """       PUT /department/1
        更新记录,参数如下：
            uid  -- 数据表的id
        """

        self.parser.add_argument("name", type=str, location="json", required=True)
        args = self.parser.parse_args()

        try:
            item = DepartmentModel.query.get(uid)
            if not item or item.is_delete:
                abort(404)
            item.name = args.name

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
        """       DELETE /department/1
        删除记录,参数如下：
            uid  -- 数据表的id
        """
        try:
            item = DepartmentModel.query.get(uid)
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
