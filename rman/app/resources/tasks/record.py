#! python3
# -*- encoding: utf-8 -*-

from flask import current_app, jsonify, abort
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.exc import SQLAlchemyError

from rman.app import db
from rman.app.common import code
from rman.app.common.utils import pretty_result
from rman.app.models.task_record import TaskRecordModel


class TaskListView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    def get(self):
        """        GET /tasks/record?page=1&size=10
        获取分页任务记录的列表，支持参数筛选,参数如下：
            case  -- 测试集名称, 用于执行的用例集合名称
            tid   -- 执行任务的时候，生成的唯一任务ID
        """

        _params = ('case',)
        self.parser.add_argument("page_num", type=int, location="args", default=1)
        self.parser.add_argument("page_size", type=int, location="args", default=10)
        self.parser.add_argument("tid", type=int, location="args", action="append")
        _ = [self.parser.add_argument(i, type=str, location="args") for i in _params]
        args = self.parser.parse_args()

        try:
            args_tid = args.tid if args.tid else []
            _or_condition = TaskRecordModel.id.in_(args_tid)
            _base_condition = {
                getattr(TaskRecordModel, i).like("%{0}%".format(args.get(i))) for i in _params if args.get(i)
            }

            all_conditions = {TaskRecordModel.is_delete == False}.union(_base_condition)
            if args_tid:
                base_condition = TaskRecordModel.query.filter(*all_conditions)\
                    .filter(_or_condition).order_by(TaskRecordModel.update_time.desc())
            else:
                base_condition = TaskRecordModel.query.filter(*all_conditions).order_by(TaskRecordModel.update_time.desc())
            pagination = base_condition.paginate(page=args.page_num, per_page=args.page_size, error_out=False)

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            items = [{
                "id": task.id,
                "case": task.case,
                "desc": task.desc,
                "tid": task.tid,
                "status": task.status,
                "report_path": task.report_path,
                "report_url": task.report_url,
                "c_time": task.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": task.update_time.strftime("%Y-%m-%d %H:%M:%S")
            } for task in pagination.items]

            result = {
                'page_num': args.page_num,
                'page_size': args.page_size,
                "total": base_condition.count(),
                "records": items
            }
            return jsonify(pretty_result(code.OK, data=result))

    def post(self):
        """        POST /tasks/record
        添加任务记录，支持批量添加任务， 参数如下
            cases  -- 添加任务，格式如：
                [{"case":'测试集名', "desc":'描述'}, {}, {}... ]
        """
        self.parser.add_argument("tasks", type=list, location="json", required=True)
        args = self.parser.parse_args()

        try:
            tasks = args.get("tasks")
            for _task in tasks:
                if not isinstance(_task, dict):
                    return jsonify(pretty_result(code.PARAM_ERROR))

            for _task in tasks:
                task = TaskRecordModel()
                task.case = _task.get("case")
                task.desc = _task.get("desc")
                db.session.add(task)
            db.session.flush()
            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return jsonify(pretty_result(code.OK))


class TaskView(Resource):

    def __init__(self):
        self.parser = RequestParser()

    @staticmethod
    def get(sid):
        """        GET /tasks/record/1
        获取任务记录,参数如下：
            sid  -- 数据表的id
        """

        try:
            task = TaskRecordModel.query.get(sid)
            if not task or task.is_delete:
                abort(404)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            result = {
                "id": task.id,
                "case": task.case,
                "desc": task.desc,
                "tid": task.tid,
                "status": task.status,
                "report_path": task.report_path,
                "report_url": task.report_url,
                "c_time": task.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "u_time": task.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }

            return jsonify(pretty_result(code.OK, data=result))

    def put(self, sid):
        """       PUT /tasks/record/1
        更新任务记录,参数如下：
            sid  -- 数据表的id
        """

        self.parser.add_argument("case", type=str, location="json", required=True)
        self.parser.add_argument("desc", type=str, location="json", required=True)
        args = self.parser.parse_args()

        try:
            task = TaskRecordModel.query.get(sid)
            if not task or task.is_delete:
                abort(404)
            task.case = args.case
            task.desc = args.desc

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
        """       DELETE /tasks/record/1
        删除任务记录,参数如下：
            sid  -- 数据表的id
        """
        try:
            task = TaskRecordModel.query.get(sid)
            if not task or task.is_delete:
                abort(404)

            task.is_delete = True
            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return pretty_result(code.OK)
