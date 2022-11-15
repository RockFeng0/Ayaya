#! python3
# -*- encoding: utf-8 -*-

import os
import time
from rtsf.p_common import FileSystemUtils, FileUtils
from rman.app.common.code import CODE_MSG_MAP
from rman.job import yaml_abs_path


def pretty_result(code, msg=None, data=None):
    """
    格式化的响应
    :param data:  本次请求的响应体
    :param code: 响应码， 默认值200，表示成功
    :param msg: 响应码的描述
    """
    return {
        'code': code,
        'msg': msg if msg is not None else CODE_MSG_MAP.get(code),
        'data': data
    }


def gen_yaml_folder(pj_name, mod_name, has_time=True):
    """ 生成yaml用例执行的工作目录
    :param pj_name: 项目名称
    :param mod_name: 模块名称
    :param has_time: 路径名是否包含时间
    :return: folder path
    """
    _mod_name = mod_name if mod_name else "_"
    if has_time:
        current_time = time.strftime("%Y-%m-%d_%H%M%S")
        pj_path = os.path.join(yaml_abs_path, pj_name, "{0}.{1}".format(_mod_name, current_time))
    else:
        pj_path = os.path.join(yaml_abs_path, pj_name, _mod_name)
    api_path = os.path.join(pj_path, "dependencies", "api")
    suite_path = os.path.join(pj_path, "dependencies", "suite")
    FileSystemUtils.mkdirs(api_path)
    FileSystemUtils.mkdirs(suite_path)
    return pj_path
