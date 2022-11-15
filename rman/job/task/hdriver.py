#! python3
# -*- encoding: utf-8 -*-


from rtsf.p_executer import TestRunner
from httpdriver.driver import HttpDriver
from rman.job import celery
# from rman.app.common.utils.email import mail
import sys
sys.path.append('/opt/deploy/rtsf/rtsf-manager')


@celery.task()
def run(case_file, task_ids=None):
    if task_ids is None:
        task_ids = []

    runner = TestRunner(runner=HttpDriver).run(case_file)
    html_report = runner.gen_html_report()
    # try:
    #     # 报告不为空
    #     if html_report[0] != 0:
    #         # 将报告发送邮件
    #         mail.sendmain(html_report, task_ids)
    # except:
    #     pass

    return {'status': 'Task completed!', 'report': html_report[0]}


if __name__ == '__main__':
    run('身份证检查正向用例.yaml')
