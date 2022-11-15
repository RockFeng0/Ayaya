#! python3
# -*- encoding: utf-8 -*-

import json
from datetime import datetime, timedelta
from flask import current_app, jsonify, abort
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import SQLAlchemyError

from rman.app import db
from rman.app.common import code
from rman.app.common.utils import pretty_result
from rman.app.models.m_department import DepartmentModel
from rman.app.models.task_conf import TaskConfigModel


class TaskConfigListView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    def get(self):
        """        GET /tasks/configs?page=1&size=10
        获取分页任务列表
        """
        _params = ('task_name',)
        self.parser.add_argument("page_num", type=int, location="args", default=1)
        self.parser.add_argument("page_size", type=int, location="args", default=10)
        self.parser.add_argument("department_id", type=int, location="args", default=0)
        _ = [self.parser.add_argument(i, type=str, location="args") for i in _params]
        args = self.parser.parse_args()

        try:
            _base_condition = {
                getattr(TaskConfigModel, i).like("%{0}%".format(args.get(i))) for i in _params if args.get(i)
            }.union({TaskConfigModel.is_delete==False})

            if args.department_id != 0:
                _base_condition = _base_condition.union({TaskConfigModel.department_id == args.department_id})

            base_condition = TaskConfigModel.query.filter(*_base_condition)\
                .order_by(TaskConfigModel.update_time.desc())
            pagination = base_condition.paginate(page=args.page_num, per_page=args.page_size, error_out=False)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            items = [{
                "id": task.id,
                "task_name": task.task_name,
                "cases": json.loads(task.cases),
                "task_ids": json.loads(task.task_ids),
                "is_timed_task": task.is_timed_task,
                "is_active": task.is_active,
                "is_run": task.is_run,
                "update_person": task.update_person,
                "department_id": task.department_id,
                "task_plan": task.task_plan.strftime("%Y-%m-%d %H:%M:%S"),
                "c_time": task.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": task.update_time.strftime("%Y-%m-%d %H:%M:%S")
            } for task in pagination.items]

            result = {
                'page_num': args.page_num,
                'page_size': args.page_size,
                "total": base_condition.count(),
                "configurations": items
            }
            return jsonify(pretty_result(code.OK, data=result))

    def post(self):
        """        POST /tasks/configs
        新增任务配置,参数如下：
            dep_id -- 部门ID
            task_name -- 任务名称
            is_timed_task -- 是否是定时任务
            task_plan -- 任务计划 e.g. '1970-01-01 08:00'
            cases -- 用例，每个{}键值对需要包含test_case表中用例的id和name
                    格式如: [{"id": xxx, "name": "xxx"},...]
        """

        self.parser.add_argument("task_name", type=str, location="json", required=True)
        self.parser.add_argument("is_timed_task", type=bool, location="json")
        self.parser.add_argument("task_plan", type=str, location="json")
        self.parser.add_argument("cases", type=list, location="json")
        self.parser.add_argument("dep_id", type=int, location="json", required=True)

        args = self.parser.parse_args()

        # 参数校验
        for i in args.cases:

            if not isinstance(i, dict):
                message = {"cases": "key-value must be in list, e.g. [{},...]"}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

            if "id" not in i.keys() or "name" not in i.keys():
                message = {"cases": "'dict' keys must contain 'id' and 'name'."}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

        try:
            if args.is_timed_task:
                _task_plan = datetime.strptime(args.task_plan, "%Y-%m-%d %H:%M")
            else:
                _task_plan = datetime.now()

            if _task_plan.__gt__(datetime.now() + timedelta(hours=12)):
                message = "请配置12小时内执行的任务."
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

        except ValueError:
            message = {"task_plan": "无效传参, 需要时间格式. e.g. '1970-01-01 08:00'"}
            return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

        # db commit
        try:
            department = DepartmentModel.query.get(args.dep_id)
            if not department or department.is_delete:
                message = {"dep_id": "无效传参,部门不存在"}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

            task_configuration = TaskConfigModel.query.filter_by(task_name=args.task_name).first()
            if task_configuration:
                message = {"task_name": "该任务已存在"}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

            task_configuration = TaskConfigModel()
            task_configuration.task_plan = _task_plan
            task_configuration.task_name = args.task_name
            task_configuration.is_timed_task = args.is_timed_task
            task_configuration.cases = json.dumps(args.cases)
            task_configuration.department_id = args.dep_id

            task_ids = []
            # for case in args.cases:
            #     task = TaskModel()
            #     task.case = case.get("name")
            #     task.desc = "__" + case.get("name")
            #     db.session.add(task)
            #     db.session.flush()
            #     task_ids.append(task.id)

            task_configuration.task_ids = json.dumps(task_ids)
            db.session.add(task_configuration)
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))


class TaskConfigView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @staticmethod
    def get(sid):
        """        GET /tasks/configs/1
        获取任务配置,参数如下：
            sid  -- 数据表的id
        """

        try:
            task_configuration = TaskConfigModel.query.get(sid)
            if not task_configuration or task_configuration.is_delete:
                abort(404)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            result = {
                "department_id": task_configuration.department_id,
                'task_name': task_configuration.task_name,
                'is_timed_task': task_configuration.is_timed_task,
                "task_plan": task_configuration.task_plan.strftime("%Y-%m-%d %H:%M:%S"),
                "cases": json.loads(task_configuration.cases)
            }
            return jsonify(pretty_result(code.OK, data=result))

    def put(self, sid):
        """        PUT /tasks/configs/1
        更新任务配置,参数如下：
            sid  -- 数据表的id
        """
        self.parser.add_argument("dep_id", type=int, location="json", required=True)
        self.parser.add_argument("task_name", type=str, location="json", required=True)
        self.parser.add_argument("is_timed_task", type=bool, location="json", required=True)
        self.parser.add_argument("task_plan", type=str, location="json", required=True)
        self.parser.add_argument("cases", type=list, location="json", required=True)

        args = self.parser.parse_args()

        # 参数校验
        for i in args.cases:

            if not isinstance(i, dict):
                message = {"cases": "key-value must be in list, e.g. [{},...]"}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

            if "id" not in i.keys() or "name" not in i.keys():
                message = {"cases": "'dict' keys must contain 'id' and 'name'."}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))
        try:
            if args.is_timed_task:
                _task_plan = datetime.strptime(args.task_plan, "%Y-%m-%d %H:%M")
            else:
                _task_plan = datetime.now()

            if _task_plan.__gt__(datetime.now() + timedelta(hours=12)):
                message = "请配置12小时内执行的任务."
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

        except ValueError:
            message = {"task_plan": "无效传参, 需要时间格式. e.g. '1970-01-01 08:00'"}
            return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

        # db commit
        try:
            department = DepartmentModel.query.get(args.dep_id)
            if not department or department.is_delete:
                abort(404)

            task_configuration = TaskConfigModel.query.get(sid)
            if not task_configuration or task_configuration.is_delete:
                abort(404)
            task_configuration.task_name = args.task_name
            task_configuration.cases = json.dumps(args.cases)
            task_configuration.is_timed_task = args.is_timed_task
            task_configuration.task_plan = _task_plan
            task_configuration.department_id = args.dep_id

            # 会造成一定冗余任务的记录，后续要优化: 看是不是在更新前，先删除原来的task_ids中的任务记录
            # 目前，量比较小，暂时不优化
            task_ids = []
            # if json.loads(task_configuration.cases) != args.cases:
            #     task_configuration.cases = json.dumps(args.cases)
            #
            #     for case in args.cases:
            #         task = TaskModel()
            #         task.case = case.get("name")
            #         task.desc = "__" + case.get("name")
            #         db.session.add(task)
            #         db.session.flush()
            #         task_ids.append(task.id)
            #     task_configuration.task_ids = json.dumps(task_ids)
            task_configuration.task_ids = json.dumps(task_ids)

            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))

    @staticmethod
    def delete(sid):
        """        DELETE /tasks/configs/1
        删除任务配置,参数如下：
            sid  -- 数据表的id
        """
        try:
            task_configuration = TaskConfigModel.query.get(sid)
            if not task_configuration or task_configuration.is_delete:
                abort(404)

            task_configuration.is_delete = True
            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return pretty_result(code.OK)
