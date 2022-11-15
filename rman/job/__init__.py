#! python3
# -*- encoding: utf-8 -*-

import sys
from celery import Celery

from rman import APP_ENV
from rman.job.conf import configs

celery = Celery("rman")
celery.config_from_object(configs[APP_ENV])
sys.path.insert(0, "") if '' not in sys.path else None
yaml_abs_path = configs[APP_ENV].YAML_CASE_PATH
