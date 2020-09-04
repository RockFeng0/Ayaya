#! python3
# -*- encoding: utf-8 -*-
import os,sys
from celery import Celery

class FactoryCelery(Celery):
    
    def init_app(self, app):
        ''' flask 工厂模式，给celery实例对象，添加 应用上下文'''
        self.conf.update(app.config)
        
        TaskBase = self.Task
        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        self.Task = ContextTask
        return self
    
    def set_path(self):
        r''' use this to fix bugs if raise error:
        
        (test_pj) C:\d_disk\auto\git\rtsf-manager>celery -A rman.manager worker --loglevel info -c 1
        Traceback (most recent call last):
          File "<string>", line 1, in <module>
          File "c:\users\58-pc\virtualenvs\test_pj\lib\site-packages\billiard\forking.py", line 459, in main
            self = load(from_parent)
        ModuleNotFoundError: No module named 'rman'
        '''
        if not '' in sys.path:
            sys.path.insert(0, "")
