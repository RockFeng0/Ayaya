#! python3
# -*- encoding: utf-8 -*-


import json
import time
import os
from rtsf.p_common import FileUtils, FileSystemUtils
from rtsf.p_exception import NotFoundError, InstanceTypeError
from rman.app import db
from rman.app.common.utils import gen_yaml_folder
# from rman.app.common.utils.other.alchemy import get_task_cases


class TSetNotFound(NotFoundError):
    pass


class TSetFileCasesError(InstanceTypeError):
    pass


class Gen(object):
    """
    Generate Http Project
    """
    TestProject, TestSuites, TestSet, TestCases, TestApis, TestSuiteApiRelation = None, None, None, None, None, None
    HttpCase = None
    DepartmentModel = None
    TaskConfigModel = None
    _ts_info = {}

    METHOD_MAP = {
        0: "GET",
        1: "POST",
        2: "PUT",
        3: "DELETE"
    }

    @classmethod
    def http_project(cls, ts_name):
        ret = {"yaml_file": "", "error_msg": ""}
        try:
            cls.ts_directory(ts_name).ts_file().api_file().suite_file()
        except TSetNotFound as e:
            ret["error_msg"] = e
        except TSetFileCasesError as e:
            ret["error_msg"] = e
        else:
            ret["yaml_file"] = cls._ts_info.get("tset_path")
        return ret

    @classmethod
    def ts_directory(cls, ts_name):
        """
        生成执行测试集工作目录
        :param ts_name: 测试集的名称
        """
        tmp_data = db.session.query(cls.TestProject, cls.TestSet) \
            .join(cls.TestSet, cls.TestSet.project_id == cls.TestProject.id) \
            .filter(cls.TestSet.name == ts_name) \
            .first()

        if not tmp_data:
            raise TSetNotFound("not found case named '{}'".format(ts_name))

        ts_data = getattr(tmp_data, cls.TestSet.__name__)
        pj_data = getattr(tmp_data, cls.TestProject.__name__)

        project_name = "{0}[{1}]".format(pj_data.name, pj_data.id)
        project_module = "all"

        # generate folder
        pj_path = gen_yaml_folder(project_name, project_module, has_time=False)

        cls._ts_info.update({
            "project_path": pj_path,
            "project_name": project_name,
            "project_module": project_module,
            "test_set_obj": ts_data,
            "current_time": time.strftime("%Y-%m-%d_%H%M%S")
        })

        return cls

    @classmethod
    def ts_file(cls, ts_info=None):
        """
        # 生成测试集文件
        # generate test set
        #        模板如下
        #         [
        #             {'project': {'name': '','module': ''}},
        #             {'case': {'name': '',
        #                       'glob_var': {},
        #                       'glob_regx': {},
        #                       'pre_command': [],
        #                       'steps': [{'request':{}}],
        #                       'post_command': [],
        #                       'verify': []
        #                       }
        #             },
        #         ]
        """
        ts_info = ts_info if ts_info else cls._ts_info
        pj_path = ts_info.get("project_path")
        ts_obj = ts_info.get("test_set_obj")

        ts_yaml = [{'project': {'name': ts_info["project_name"], 'module': ts_info["project_module"]}}]

        ids = [ts_obj.id]

        conditions = {cls.TestCases.case_type == 1001, cls.TestCases.id.in_(ids)}
        cases = db.session.query(cls.TestCases, cls.HttpCase) \
            .outerjoin(cls.HttpCase, cls.TestCases.case_id == cls.HttpCase.id) \
            .filter(*conditions).all()

        # cases = get_task_cases(ts_obj.id)
        # if isinstance(cases, dict):
        #     raise TSetFileCasesError("get_task_cases: {0}".format(cases))
        if len(cases) != len(ids):
            error_msg = "Taskconfig[{0}]中的cases字段中id{1},存在关联错误的httpcase.".format(ts_obj.id, ids)
            raise TSetFileCasesError(error_msg)

        for cs in cases:
            tc_data = getattr(cs, cls.TestCases.__name__)
            hc_data = getattr(cs, cls.HttpCase.__name__)

            _case = {}
            tc_data_name = FileSystemUtils.get_legal_filename(str(tc_data.name))
            if tc_data.case_type == 1002:
                _case = {
                    "id": tc_data.id,
                    "name": tc_data_name,
                    "call_api": tc_data.call_api,
                }

            if tc_data.case_type == 1003:
                _case = {
                    "id": tc_data.id,
                    "name": tc_data_name,
                    "call_suite": tc_data.call_suite,
                }

            if tc_data.case_type == 1001:
                _case = {
                    "id": tc_data.id,
                    "name": tc_data_name,
                    # "steps": [{"request": GenHttpAccessories.requests(hc_data)}]
                }
                _case.update(GenHttpAccessories.global_vars(hc_data))
                _case.update(GenHttpAccessories.pre_command(hc_data))
                _case.update(GenHttpAccessories.steps(hc_data))
                _case.update(GenHttpAccessories.post_command(hc_data))
                _case.update(GenHttpAccessories.verify(hc_data))
                _case = {k: v for k, v in _case.items() if v}

            ts_yaml.append({"case": _case})

        ts_yaml_path = os.path.join(pj_path, "{0}.yaml".format(FileSystemUtils.get_legal_filename(ts_obj.name)))
        cls._ts_info.update({"tset_path": ts_yaml_path})

        FileUtils._dump_yaml_file(ts_yaml, ts_yaml_path)
        return cls

    @classmethod
    def api_file(cls, ts_info=None):
        """
        # 生成依赖的api文件
        # generate api
        #        模板如下
        #         [
        #             {'api':
        #                 {
        #                     'def': '',
        #                     'pre_command': [],
        #                     'steps': [{'request': {}},],
        #                     'post_command': [],
        #                     'verify': []
        #                 }
        #             },
        #         ]
        """
        # todo
        return cls

    @classmethod
    def suite_file(cls, ts_info=None):
        """
        # 生成测试套件文件
        # generate suite
        #        模板如下
        #         [
        #             {'project': {'def': ''}},
        #             {'case': {'name': '',
        #                       'glob_var': {},
        #                       'glob_regx': {},
        #                       'pre_command': [],
        #                       'steps': [{'request':{}}],
        #                       'post_command': [],
        #                       'verify': []
        #                       }
        #             },
        #         ]
        """
        # todo
        return cls


class GenHttpAccessories(object):

    @staticmethod
    def steps(http_case_data):
        return {"steps": [{"request": GenHttpAccessories.requests(http_case_data)}]}

    @staticmethod
    def requests(http_case_data):
        headers = GenHttpAccessories.headers(http_case_data)

        # 默认是params参数请求
        req_type = "params"
        for k, v in headers.items():
            if k.lower() == "content-type" and v.lower() == "application/json":
                req_type = "json"
                break

        return {
            "url": http_case_data.url if http_case_data else "",
            # "method": hc_data.method if hc_data else "",
            # "headers": json.loads(http_case_data.headers) if http_case_data.headers else {},
            # "params": json.loads(http_case_data.body) if http_case_data.body else {},
            "method": Gen.METHOD_MAP[http_case_data.method],
            "headers": headers,
            req_type: GenHttpAccessories.body(http_case_data),
            "files": json.loads(http_case_data.files) if http_case_data.files else {},
        }

    @staticmethod
    def global_vars(http_case_data):
        _global_vars = ("glob_var", "glob_regx")
        # return {
        #     i: json.loads(getattr(http_case_data, i)) if getattr(http_case_data, i) else {} for i in _global_vars
        # }
        return {i: {} for i in _global_vars}

    @staticmethod
    def global_vars_bak(http_case_data):
        result = {}
        _global_vars = ("glob_var", "glob_regx")
        for i in _global_vars:
            result[i] = {}

            if not getattr(http_case_data, i):
                continue

            tmp_data = json.loads(getattr(http_case_data, i))

            if not isinstance(tmp_data, list):
                raise Exception("invalid %s format." % i)

            for kv in tmp_data:
                k, v = kv.get("key"), kv.get("value")
                if not k:
                    continue
                result[i][k] = v
        return result

    @staticmethod
    def pre_command(http_case_data):
        # 预留
        return {"pre_command": []}

    @staticmethod
    def headers(http_case_data):
        result = {}
        headers_data = json.loads(http_case_data.headers) if http_case_data.headers else []
        if not isinstance(headers_data, list):
            raise Exception("invalid http header format.")

        for hd in headers_data:
            ky, val = hd.get("key"), hd.get("value")
            if not ky:
                continue
            result[ky] = val
        return result

    @staticmethod
    def body(http_case_data):
        result = {}
        body_data = json.loads(http_case_data.body) if http_case_data.body else []

        if not isinstance(body_data, list):
            raise Exception("invalid http body format.")

        for bd in body_data:
            ky, val = bd.get("key"), bd.get("value")
            if not ky:
                continue
            result[ky] = val
        return result

    @staticmethod
    def post_command(http_case_data):
        result = {"post_command": []}

        post_data = json.loads(http_case_data.post_command) if http_case_data.post_command else []
        if not isinstance(post_data, list):
            raise Exception("invalid post_command format.")

        for pd in post_data:
            var, frm, tp = pd.get("key"), pd.get("value"), pd.get("type")
            # 如果是json，那么DyJsonData需要frm为sequence; 否则，DyStrData关键字就需要frm为正则表达式
            key_word = "DyJsonData" if tp == "json" else "DyStrData"
            result["post_command"].append("${%s(%s, %s)}" % (key_word, var, frm))
        return result

    @staticmethod
    def verify(http_case_data):
        result = {"verify": []}
        verify_data = json.loads(getattr(http_case_data, "verify")) if getattr(http_case_data, "verify") else []
        for kv in verify_data:
            result["verify"].append("${VerifyContain(%s)}" % kv.get("value", ""))
        return result

