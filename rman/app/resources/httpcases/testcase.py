#! python3
# -*- encoding: utf-8 -*-

import json
from flask import current_app, jsonify, abort
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError

from rman.app import db
from rman.app.common import code
from rman.app.common.utils import pretty_result

from rman.app.models.m_department import DepartmentModel
from rman.app.models.m_project import ProjectModel
from rman.app.models.m_module import ModuleModel
from rman.app.models.test_case import TestCaseModel
from rman.app.models.http_case.api import HttpApiModel
from rman.app.models.http_case.http_step import HttpStepModel, METHOD_TYPE_MAP


class HttpCaseListView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @login_required
    def get(self):
        """        GET /httpcase?page=1&size=10
        获取分页任务记录的列表，支持参数筛选,参数如下：
            name  -- 项目名称
        """

        _params = ('name', 'url')
        self.parser.add_argument("dep_id", type=int, location="args")
        self.parser.add_argument("page_num", type=int, location="args", default=1)
        self.parser.add_argument("page_size", type=int, location="args", default=10)
        _ = [self.parser.add_argument(i, type=str, location="args") for i in _params]
        args = self.parser.parse_args()

        if not args.dep_id:
            return jsonify(pretty_result(code.PARAM_ERROR, "部门ID未传入"))

        try:
            _base_condition = {
                getattr(HttpStepModel, i).like("%{0}%".format(args.get(i))) for i in _params if args.get(i)
            }

            all_conditions = {
                DepartmentModel.is_delete == False,
                DepartmentModel.id == int(args.dep_id),
                ProjectModel.is_delete == False,
                TestCaseModel.is_delete == False,
                ModuleModel.is_delete == False,
                HttpStepModel.is_delete == False,
            }.union(_base_condition)

            base_condition = db.session.query(
                DepartmentModel.name,
                ProjectModel.name,
                ModuleModel.name,
                TestCaseModel.name,
                TestCaseModel.responsible,
                HttpStepModel.update_time
            ) \
                .outerjoin(ProjectModel, DepartmentModel.id == ProjectModel.department_id) \
                .join(ModuleModel, ProjectModel.id == ModuleModel.project_id)\
                .join(TestCaseModel, ModuleModel.id == TestCaseModel.module_id)\
                .join(HttpStepModel, TestCaseModel.id == HttpStepModel.testcase_id)\
                .filter(*all_conditions).order_by(HttpStepModel.update_time.desc())

            pagination = base_condition.paginate(page=args.page_num, per_page=args.page_size, error_out=False)

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            keys = ('dep_name', 'pj_name', 'mod_name', 'case_name', 'case_responsible', 'update_time')
            items = [dict(zip(keys, item)) for item in pagination.items]
            for index in range(len(items)):
                items[index]['update_time'] = items[index]['update_time'].strftime("%Y-%m-%d %H:%M:%S")

            result = {
                'page_num': args.page_num,
                'page_size': args.page_size,
                "total": base_condition.count(),
                "records": items
            }
            return jsonify(pretty_result(code.OK, data=result))

    def post(self):
        """        POST /httpcase
        记录新增，支持批量， 参数如下
            users  -- 添加任务，格式如：
                [{"pj_id":'xxx', "mod_name":'xxx',...}, {}, {}... ]
        """
        # copy api case  to do
        self.parser.add_argument("items", type=list, location="json", required=True)
        args = self.parser.parse_args()

        try:
            items = args.get("items")
            for item in items:
                if not isinstance(item, dict):
                    return jsonify(pretty_result(code.PARAM_ERROR))

            for _item in items:
                module = db.session.query(ModuleModel).filter(
                    ModuleModel.project_id == int(_item.get("pj_id")),
                    ModuleModel.name == _item.get("mod_name")
                ).first()

                if not module:
                    module = ModuleModel()
                    module.name = _item.get("mod_name")
                    module.project_id = int(_item.get("pj_id"))
                    db.session.add(module)
                    db.session.flush()

                case = TestCaseModel()
                case.name = _item.get("case_name")
                case.desc = _item.get("desc")
                case.responsible = _item.get("responsible")
                case.tester = _item.get("tester")
                case.module_id = module.id
                db.session.add(case)
                db.session.flush()

                hcase_kwargs = {"name": _item.get("case_name"), "testcase_id": case.id}
                _ = [hcase_kwargs.update({i: json.dumps(_item.get(i, {}))}) for i in
                     ("glob_var", "glob_regx", "headers", "body", "files")]
                _ = [hcase_kwargs.update({i: json.dumps(_item.get(i, []))}) for i in
                     ("pre_command", "post_command", "verify")]
                hcase_kwargs.update({"url": _item.get("url"), "method": METHOD_TYPE_MAP[_item.get("method").upper()]})

                _step = HttpStepModel(**hcase_kwargs)
                db.session.add(_step)
                db.session.flush()
            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))


class HttpCaseView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @staticmethod
    @login_required
    def get(uid):
        """        GET /httpcase/1
        获取记录,参数如下：
            uid  -- 数据表的id
        """

        try:
            case = TestCaseModel.query.get(uid)
            if not case or case.is_delete:
                abort(404)

            result = {
                "id": case.id,
                "name": case.name,
                "desc": case.desc,
                "responsible": case.responsible,
                "tester": case.tester,
                "steps": []
            }

            steps = db.session.query(HttpStepModel).filter_by(testcase_id=uid, is_delete=0).all()
            if not steps:
                abort(404)

            result["steps"] = [{
                "step_id": step.id,
                "step_name": step.name,
                "glob_var": step.glob_var,
                "glob_regx": step.glob_regx,
                "pre_command": step.pre_command,
                "url": step.url,
                "method": step.method,
                "headers": step.headers,
                "body": step.body,
                "files": step.files,
                "post_command": step.post_command,
                "verify": step.verify,
                "c_time": step.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": step.update_time.strftime("%Y-%m-%d %H:%M:%S")
            } for step in steps]

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK, data=result))

    @login_required
    def put(self, uid):
        """       PUT /httpcase/1
        更新记录,参数如下：
            uid  -- 数据表的id
        """

        self.parser.add_argument("name", type=str, location="json", required=True)
        self.parser.add_argument("desc", type=str, location="json", required=False)
        self.parser.add_argument("responsible", type=str, location="json", required=False)
        self.parser.add_argument("tester", type=str, location="json", required=False)
        self.parser.add_argument("module_id", type=int, location="json", required=True)
        args = self.parser.parse_args()

        try:
            case = TestCaseModel.query.get(uid)
            if not case or case.is_delete:
                abort(404)

            _ = [setattr(case, k, v) for k, v in args.items()]

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
        """       DELETE /httpcase/1
        删除记录,参数如下：
            uid  -- 数据表的id
        """
        try:
            item = TestCaseModel.query.get(uid)
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


class HttpStepView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @login_required
    def put(self, uid):
        """       PUT /step/1
        更新记录,参数如下：
            uid  -- 数据表的id
        """

        dict_args = ("glob_var", "glob_regx", "headers", "body", "files")
        list_args = ("pre_command", "post_command", "verify")
        str_args = ("url", "method")
        self.parser.add_argument("name", type=str, location="json", required=True)
        _ = [self.parser.add_argument(i, type=str, location="json") for i in str_args]
        _ = [self.parser.add_argument(i, type=list, location="json") for i in list_args]
        _ = [self.parser.add_argument(i, type=dict, location="json") for i in dict_args]
        args = self.parser.parse_args()

        try:
            step = HttpStepModel.query.get(uid)
            if not step or step.is_delete:
                abort(404)

            step.name = args.name
            step.url = args.url
            step.method = METHOD_TYPE_MAP[args.method.upper()]
            _ = [setattr(step, i, json.dumps(args.get(i, {}))) for i in dict_args]
            _ = [setattr(step, i, json.dumps(args.get(i, []))) for i in list_args]

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
        """       DELETE /step/1
        删除记录,参数如下：
            uid  -- 数据表的id
        """
        try:
            item = HttpStepModel.query.get(uid)
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
