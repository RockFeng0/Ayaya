#! python3
# -*- encoding: utf-8 -*-


class Config(object):
    CELERY_TIMEZONE = 'Asia/Shanghai'

    # 有些情况下可以防止死锁
    CELERYD_FORCE_EXECV = True

    # BROKER_TRANSPORT_OPTIONS 如果设置的过小，延时任务有可能被多次反复执行； 的默认值是3600秒
    BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 43200}

    # 每个worker最多执行100个任务被销毁，可以防止内存泄漏
    CELERYD_MAX_TASKS_PER_CHILD = 100

    CELERY_IMPORTS = (
        "rman.job.task.hdriver",
        "rman.job.task.demo",
    )


class ProdConfig(Config):
    BROKER_URL = 'redis://172.16.49.102:6379'
    CELERY_RESULT_BACKEND = 'redis://172.16.49.102:6379'
    YAML_CASE_PATH = "/opt/deploy/rtsf/buffer/rman_gen"


class DevConfig(Config):
    BROKER_URL = 'redis://:123456@localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://:123456@localhost:6379'
    YAML_CASE_PATH = r"C:\d_disk\auto\buffer\ch_rman"


configs = {"production": ProdConfig, "testing": DevConfig}
