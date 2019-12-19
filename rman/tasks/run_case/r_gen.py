#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.tasks.run_case.r_gen

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.tasks.run_case.r_gen,  v1.0 2019年12月10日
    FROM:   2019年12月10日
********************************************************************
======================================================================

Provide a function for the automation test

'''

import json, time, os
from rtsf.p_common import FileSystemUtils, FileUtils
from rman.app.manager.models import TestSet, TestCases, TestApis, TestSuiteApiRelation
from rman.app.httpcase.models import HttpCaseQuerys
# from rman.tasks import yaml_abs_path
from rman.app import celery
yaml_abs_path = celery.conf.get("YAML_CASE_PATH")

def gen_http_project(case_name):
        
    _query = HttpCaseQuerys.j_project_set()
    _query_case = HttpCaseQuerys.j_tcase_hcase()
    _query_api = HttpCaseQuerys.j_api_hcase()
    _query_suite = HttpCaseQuerys.t_suite()
    _query_suite_relation_api = HttpCaseQuerys.j_suite_relation_api()
    
    tmp_data  = _query.filter(TestSet.name == case_name).first()
        
    if tmp_data:
        tset_data = tmp_data.TestSet
        pj_data = tmp_data.TestProject
        
        # generate folder
        current_time = time.strftime("%Y-%m-%d_%H%M%S")
        folder_info = {
            "pj_id": pj_data.id,   
            "pj_name": pj_data.name,
            "pj_module_name": pj_data.module,        
            "tset_name": tset_data.name,
            "current_time": current_time
        }
        pj_path = os.path.join(yaml_abs_path, pj_data.name, "{0}.{1}".format(pj_data.module, current_time))
        api_path = os.path.join(pj_path, "dependencies", "api")
        suite_path = os.path.join(pj_path, "dependencies", "suite")
        FileSystemUtils.mkdirs(api_path)
        FileSystemUtils.mkdirs(suite_path)
        
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
        tset_info = [{'project': {'name': pj_data.name, 'module': pj_data.module}}]
        cases = _query_case.filter(TestCases.test_set_id == tset_data.id).all()        
        for cs in cases:
            tc_data = cs.TestCases
            hc_data = cs.HttpCase
            
            if tc_data.call_api:
                _case = {
                        "id": tc_data.id,
                        "name": tc_data.name,
                        "call_api": tc_data.call_api,
                    }
            elif tc_data.call_suite:
                _case = {
                        "id": tc_data.id,
                        "name": tc_data.name,
                        "call_suite": tc_data.call_suite,
                    }
            else:
                _case = {
                        "id": tc_data.id,
                        "name": tc_data.name,
                        
                        "steps": [{
                            "request": {
                                "url": hc_data.url if hc_data else "",
                                "method": hc_data.method if hc_data else "",
                                
                                "headers": json.loads(hc_data.headers) if hc_data else {},
                                "params": json.loads(hc_data.body) if hc_data else {},
                                "files": json.loads(hc_data.files) if hc_data else {},
                            },
                        }]
                    }                 
            
                _case.update({i: json.loads(getattr(hc_data, i)) if hc_data else {} for i in ("glob_var", "glob_regx")})
                _case.update({i: json.loads(getattr(hc_data, i))  if hc_data else [] for i in ("pre_command", "post_command", "verify")})
            
                _case = {k:v for k,v in _case.items() if v}
            tset_info.append({"case":_case})
            
        tset_path = os.path.join(pj_path, "{0}.yaml".format(tset_data.name))
        FileUtils._dump_yaml_file(tset_info, tset_path)
        
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
        apis_info = []
        api_datas = _query_api.filter(TestApis.project_id == pj_data.id).all()        
        for pg in api_datas:
            api_data = pg.TestApis
            hc_data = pg.HttpCase
            _api = {
                "id": api_data.id,
                "api_def": api_data.api_def,
                "steps": [{
                    "request": {
                        "url": hc_data.url if hc_data else "",
                        "method": hc_data.method if hc_data else "",
                        
                        "headers": json.loads(hc_data.headers) if hc_data else {},
                        "params": json.loads(hc_data.body) if hc_data else {},
                        "files": json.loads(hc_data.files) if hc_data else {},
                    },
                }]
            }     
            _api.update({i: json.loads(getattr(hc_data, i)) if hc_data else {} for i in ("glob_var", "glob_regx")})
            _api.update({i: json.loads(getattr(hc_data, i))  if hc_data else [] for i in ("pre_command", "post_command", "verify")})                        
            
            _api = {k:v for k,v in _api.items() if v}
            apis_info.append({"api":_api})
        
        if apis_info:
            FileUtils._dump_yaml_file(apis_info, os.path.join(api_path, "apis.yaml"))
        
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
        suites_info = []
        suite_datas = _query_suite.filter_by(project_id = pj_data.id).all()
        for suite_data in suite_datas:
            _suite = [{'project': {'def': suite_data.suite_def}}]
            
            case_datas = _query_suite_relation_api.filter(TestSuiteApiRelation.suite_id == suite_data.id).all()
            for name, api_def in case_datas:                
                _suite.append({"case": {"name": name, "api": api_def}})            
            suites_info.append(_suite)
                
        for suite in suites_info:
            _suite_path = os.path.join(suite_path, "suite_%d.yaml".format(suite_data.id))
            FileUtils._dump_yaml_file(suite, _suite_path)
        
#         print("############# case name:  %s" %case_name)
#         print("#########\n", yaml_abs_path)
#         print("folder info: \n", folder_info)
#         print("tset info: \n", tset_info)
#         print("apis info: \n", apis_info)
#         print("suites info: \n", suites_info)
    return tset_path