#! python3
# -*- encoding: utf-8 -*-

import os
import io
import json
from datetime import datetime, timedelta
from flask_restful.reqparse import RequestParser
from flask import current_app, jsonify, abort, url_for, send_file, make_response
from sqlalchemy.exc import SQLAlchemyError

from rman.app import db
from rman.app.common import code
from rman.app.common.utils import pretty_result
from rman.app.routes.views.tasks import tasks

from rman.app.models.task_record import TaskModel, STATUS_MAP
from rman.app.models.task_conf import TaskConfigModel
from rman.app.models.m_department import DepartmentModel
from rman.app.models.m_project import ProjectModel
from rman.app.models.test_case import TestCaseModel as TestSetModel
from rman.app.models.test_step import TestStepModel as TestCaseModel
from rman.app.models.http_case.case import HttpCaseModel
# from rman.app.models.ut_rman_testapi import TestApiModel
# from rman.app.models.ut_rman_testsuite import TestSuiteModel
# from rman.app.models.ut_rman_suite__api import SuiteApiRelationModel

from rman.job.gen import Gen
# from rman.job.gens import Gen  # 全部导出 的话用这个
from rman.job.task import demo, hdriver

import sys
sys.path.append('/opt/deploy/rtsf/rtsf-manager')


# class GenV1(Gen):
#     TestProject = ProjectModel
#     TestSuites = TestSuiteModel
#     TestSet = TestSetModel
#     TestCases = TestCaseModel
#     setattr(TestCases, "call_api", TestCases.api_id)
#     setattr(TestCases, "call_suite", TestCases.suite_id)
#     setattr(TestCases, "call_manunal_id", TestCases.case_id)
#     TestApis = TestApiModel
#     setattr(TestApis, "call_manunal_id", TestApis.case_id)
#     TestSuiteApiRelation = SuiteApiRelationModel
#     HttpCase = HttpCaseModel


class GenV2(Gen):
    TestProject = ProjectModel
    TestSuites = TestSuiteModel
    TestSet = TestSetModel
    TestCases = TestCaseModel
    TestApis = TestApiModel
    TestSuiteApiRelation = SuiteApiRelationModel
    HttpCase = HttpCaseModel
    DepartmentModel = DepartmentModel
    TaskConfigModel = TaskConfigModel


class Demo(object):

    @staticmethod
    @tasks.route('/demo', methods=['GET'])
    def add():
        # GET /tasks/demo
        parser = RequestParser()
        parser.add_argument("seconds", type=int, location="args", default=10)
        args = parser.parse_args()

        async_task = demo.add.apply_async(args=[2, 8], eta=datetime.utcnow() + timedelta(seconds=args.seconds))
        return {"task id": async_task.id, "delay seconds": args.seconds}

    @staticmethod
    @tasks.route('/demo/status/<string:tid>', methods=['GET'])
    def demo_status(tid):
        # GET /tasks/demo/status/415644d0-c7ba-4d9d-8c40-d548f31899e2
        print("++++++++++++")
        try:
            back_end = demo.add.AsyncResult(tid)
        except Exception as e:
            print(e)
            return "---"
        status = {"state": back_end.state}

        if back_end.state == 'PENDING':
            status["message"] = "wait for the job finish."

        elif back_end.state == 'FAILURE':
            status["message"] = "something went wrong in the background job: " + str(back_end.info)

        else:
            status["message"] = "job finished."
            status["result"] = back_end.result

        return status

    @staticmethod
    @tasks.route('/demo/deactive/<string:tid>', methods=['GET'])
    def demo_deactive(tid):
        hdriver.celery.control.revoke(tid, terminate=True)
        return jsonify(pretty_result(code.OK))


class TasksView(object):
    __prefix_url = "/api/v1.0/tasks"

    @staticmethod
    @tasks.route('/gen')
    def debug_gen():
        """ 调试生成yaml用例
        GET /tasks/gen?tset_name=测试
        """
        parser = RequestParser()
        parser.add_argument("tset_name", type=str, required=True)
        args = parser.parse_args()

        if args.tset_name != "all":
            # ret = GenV1.http_project(args.tset_name)
            ret = GenV2.http_project(args.tset_name)
            yaml_file, error_msg = ret.get("yaml_file"), ret.get("error_msg")
            if os.path.isfile(yaml_file):
                return pretty_result(code.OK, data=yaml_file)
            else:
                current_app.logger.error("无效脚本, 错误信息: {0}".format(error_msg))
                return pretty_result(code.UNKNOWN_ERROR, msg="无效脚本, 错误信息: {0}".format(error_msg))
        # 全部导出  参数填 all 时
        cases = db.session.query(GenV2.TestSet).filter(GenV2.TestSet.is_delete == '0').all()
        result = {
            "success": {
                "total": 0,
                "names": []
            },
            "error": {
                "total": 0,
                "names": []
            },
        }
        for case in cases:
            ret = GenV2.http_project(case.name)
            yaml_file, error_msg = ret.get("yaml_file"), ret.get("error_msg")
            if os.path.isfile(yaml_file):
                result["success"]["names"].append(yaml_file)
                result["success"]["total"] += 1
            else:
                result["error"]["names"].append({case.name: str(error_msg)})
                result["error"]["total"] += 1
        return pretty_result(code.OK, data=result)

    @staticmethod
    @tasks.route('/active')
    def active():
        """ 激活指定的任务配置，延时执行
        GET /tasks/active?cid=1
        """
        parser = RequestParser()
        parser.add_argument("cid", type=int, location="args")
        args = parser.parse_args()

        try:
            task_config = TaskConfigModel.query.get(args.cid)
            if not task_config or task_config.is_delete:
                abort(404)
            if not task_config.is_timed_task:
                return jsonify(pretty_result(code.PARAM_ERROR, msg="非定时任务."))

            if task_config.task_plan.__lt__(datetime.now()):
                message = "任务已过期."
                return jsonify(pretty_result(code.VALUE_ERROR, msg=message))
            utc_eta = datetime.utcfromtimestamp(datetime.timestamp(task_config.task_plan))

            task = TaskModel()
            task.case = task_config.task_name
            task.desc = "延时执行__" + task_config.task_name
            db.session.add(task)
            db.session.flush()
            task_config.task_ids = json.dumps([task.id])

            TasksView.__execute_task(json.loads(task_config.task_ids), eta=utc_eta)
            task_config.is_active = True
            task_config.is_run = True
            db.session.flush()
            db.session.commit()

        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return pretty_result(code.OK)

    @staticmethod
    @tasks.route('/deactive')
    def deactive():
        """ 终止任务运行
        GET /tasks/deactive?cid=1
        """
        parser = RequestParser()
        parser.add_argument("cid", type=int, location="args")
        args = parser.parse_args()

        try:
            task_config = TaskConfigModel.query.get(args.cid)
            if not task_config or task_config.is_delete:
                abort(404)

            if not task_config.task_ids:
                return pretty_result(code.OK)

            TasksView.__revoke_task(json.loads(task_config.task_ids))
            task_config.is_active = False
            task_config.is_run = True
            db.session.flush()
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return pretty_result(code.OK)


    @staticmethod
    @tasks.route('/run')
    def hdriver():
        """ 批量驱动指定的任务，立即执行
        GET /tasks/run?cid=1&cid=2
        """
        parser = RequestParser()
        parser.add_argument("cid", type=str, action="append")
        args = parser.parse_args()
        if not args.cid:
            message = {"cid": "params中缺少必需的参数"}
            return jsonify(pretty_result(code.PARAM_ERROR, msg=message))

        task_config_objs = []
        for _id in args.cid:
            task_config = TaskConfigModel.query.filter_by(id=_id, is_delete=False).first()
            if not task_config:
                message = {"cid": "未找到[{0}]任务配置".format(_id)}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))
            task_config_objs.append(task_config)

        _task_ids = []
        for task_config_obj in task_config_objs:
            print(task_config_obj)
            task = TaskModel()
            task.case = task_config_obj.task_name
            task.desc = "立即执行__" + task_config_obj.task_name
            db.session.add(task)
            db.session.flush()
            task_config_obj.task_ids = json.dumps([task.id])
            _task_ids.append(task.id)
            print(_task_ids)

        TasksView.__execute_task(_task_ids)
        return jsonify(pretty_result(code.OK))

    @staticmethod
    @tasks.route('/status')
    def status():
        """ 批量获取任务的执行状态
        GET /tasks/status?tid=1&tid=2
        """
        parser = RequestParser()
        parser.add_argument("tid", type=str, action="append")
        args = parser.parse_args()

        __tasks = []
        for _id in args.tid:
            task = TaskModel.query.filter_by(id=_id, is_delete=False).first()
            if not task:
                return jsonify(pretty_result(code.PARAM_ERROR, msg="nod found id={}".format(_id)))
            __tasks.append(task)

        results = []
        for task in __tasks:
            _task_res = {
                "id": task.id,
                "status": task.status,
                "case_name": task.case,
                "state": "",
                "message": STATUS_MAP[task.status]
            }

            if task.status not in [4, 5, 6, 0]:
                async_task = hdriver.run.AsyncResult(task.tid)
                print(task.tid)
                _task_res["state"] = async_task.state

                if async_task.state == 'PENDING':
                    _task_res["message"] = "执行中."
                    task.status = 1
                    task.report_url = ""
                elif async_task.state == 'FAILURE':
                    _task_res["message"] = "执行失败: " + str(async_task.info)
                    task.status = 3
                    task.report_url = ""
                else:
                    _task_res["message"] = "执行成功."
                    task.report_path = async_task.info.get("report")
                    task.status = 2
                    task.report_url = url_for("tasks.report", task_id=task.id, _external=True)
            results.append(_task_res)

        db.session.flush()
        db.session.commit()
        return jsonify(pretty_result(code.OK, data=results))


    @staticmethod
    @tasks.route('/gettid')
    def gettid_from_taskcid():
        parser = RequestParser()
        parser.add_argument("cid", type=str, action="append")
        args = parser.parse_args()
        task_config_objs = []
        for _id in args.cid:
            # task_config = TaskConfigModel.query.filter_by(id=_id, is_delete=False).first()
            task_config = db.session.query(TaskConfigModel).filter(TaskConfigModel.id == _id).all()
            if not task_config:
                message = {"cid": "未找到[{0}]任务配置".format(_id)}
                return jsonify(pretty_result(code.PARAM_ERROR, msg=message))
            task_config_objs.append(task_config)
            for task_config_obj in task_config_objs:
                task_ids1 = json.loads(task_config_obj[0].task_ids)
                print(task_config_obj[0].task_ids)
                __tasks = []
                for _id in task_ids1:
                    tid=_id
                    task = TaskModel.query.filter_by(id=_id, is_delete=False).first()
                    if not task:
                        return jsonify(pretty_result(code.PARAM_ERROR, msg="nod found id={}".format(_id)))
                    __tasks.append(task)

                results = []
                for task in __tasks:
                    _task_res = {
                        "id": task.id,
                        "status": task.status,
                        "case_name": task.case,
                        "state": "",
                        "message": STATUS_MAP[task.status]
                    }

                    if task.status not in [4, 5, 6, 0]:
                        print(1)
                        async_task = hdriver.run.AsyncResult(task.tid)
                        _task_res["state"] = async_task.state

                        if async_task.state == 'PENDING':
                            _task_res["message"] = "执行中."
                            task.status = 1
                            task.report_url = ""
                        elif async_task.state == 'FAILURE':
                            _task_res["message"] = "执行失败: " + str(async_task.info)
                            task.status = 3
                            task.report_url = ""
                        else:
                            _task_res["message"] = "执行成功."
                            task.report_path = async_task.info.get("report")
                            task.status = 2
                            task.report_url = url_for("tasks.report", task_id=task.id, _external=True)
                    results.append(_task_res)

                db.session.flush()
                db.session.commit()



        return jsonify(pretty_result(code.OK))



    @staticmethod
    @tasks.route('/report', methods=["GET"])
    def report():
        """ 获取任务报告
        GET /tasks/report?task_id=32342
        """
        parser = RequestParser()
        parser.add_argument("task_id", type=str, required=True)
        args = parser.parse_args()

        try:
            task = TaskModel.query.get(args.task_id)
            if not task or task.is_delete or not os.path.isfile(task.report_path):
                abort(404)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            return send_file(task.report_path)

    @staticmethod
    @tasks.route('/caselogs/<log>')
    def case_log(log):
        """ 获取任务执行的日志
        GET /tasks/caselogs/xxx.log?task_id=32342
        """
        parser = RequestParser()
        parser.add_argument("task_id", type=str, required=True)
        args = parser.parse_args()

        try:
            task = TaskModel.query.get(args.task_id)
            if not task or task.is_delete or not os.path.isfile(task.report_path):
                abort(404)
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            return pretty_result(code.DB_ERROR, '数据库错误！')
        else:
            report_abs_path = os.path.dirname(task.report_path)
            lg = os.path.join(report_abs_path, 'caselogs/%s' % log)
            resp = make_response(io.open(lg, 'r', encoding='utf-8').read())
            resp.headers["Content-type"] = "text/plain;charset=UTF-8"
            return resp

    @staticmethod
    def __execute_task(task_ids, **options):
        """ 用于执行TaskModel表中的任务

        :param task_ids:  list结构，值为ut_rman_task中的id, e.g. [1,2,3]
        :param **options: apply_async中的可选参数，需参见celery官网
        :return:
        """
        __tasks = []
        for _id in task_ids:
            task = TaskModel.query.filter_by(id=_id, is_delete=False).first()
            if not task:
                return jsonify(pretty_result(code.PARAM_ERROR, msg="not found tid={}".format(_id)))
            __tasks.append(task)

        for task in __tasks:
            # ret = GenV1.http_project(task.case)
            ret = GenV2.http_project(task.case)
            yaml_file, error_msg = ret.get("yaml_file"), ret.get("error_msg")

            task.report_path = ""
            task.report_url = ""
            if os.path.isfile(yaml_file):
                try:
                    async_task = hdriver.run.apply_async(args=(yaml_file, task_ids), **options)
                    task.tid = async_task.id
                    task.status = 1
                except ConnectionError:
                    # Redis server not connected
                    task.status = 5
            else:
                # 0-未执行, 1-执行中, 2-执行成功, 3-执行失败, 4-无效脚本 , 5-redis服务异常
                current_app.logger.error("无效脚本, 错误信息: {0}".format(error_msg))
                task.status = 4
        db.session.flush()
        db.session.commit()

    @staticmethod
    def __revoke_task(task_model_ids, **kwargs):
        """ 用于终止TaskModel表中的任务

        :param task_model_ids:  id list from TaskModel, e.g. [1,2,3]
        :param **kwargs: revoke中的可选参数，需参见celery官网
        :return:
        """
        __tasks = []
        for _id in task_model_ids:
            task = TaskModel.query.filter_by(id=_id, is_delete=False).first()
            if not task:
                return jsonify(pretty_result(code.PARAM_ERROR, msg="not found tid={}".format(_id)))
            __tasks.append(task)

        for task in __tasks:
            hdriver.celery.control.revoke(task.tid, terminate=True, **kwargs)
            task.status = 6
            task.report_url = ""
        db.session.flush()
        db.session.commit()

