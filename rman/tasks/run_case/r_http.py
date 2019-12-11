#! python3
# -*- encoding: utf-8 -*-
'''
Current module: rman.tasks.run_case.r_http

Rough version history:
v1.0    Original version to use

********************************************************************
    @AUTHOR:  Administrator-Bruce Luo(罗科峰)
    MAIL:     luokefeng@163.com
    RCS:      rman.tasks.run_case.r_http,  v1.0 2019年12月5日
    FROM:   2019年12月5日
********************************************************************
======================================================================

Provide a function for the automation test

'''

from rman.tasks import celery

from rtsf.p_executer import TestRunner
from httpdriver.driver import HttpDriver


@celery.task(bind=True)
def test_http_case(self, case_file):
    runner = TestRunner(runner = HttpDriver).run(case_file)
    html_report = runner.gen_html_report()    
    return {'status': 'Task completed!','report': html_report[0]}
    