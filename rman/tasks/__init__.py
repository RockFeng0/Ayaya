from celery import Celery
from rman.tasks.celeryconfig import configs
from rman import APP_ENV

celery = Celery("rman")
celery.config_from_object(configs[APP_ENV])

yaml_abs_path = configs[APP_ENV].YAML_CASE_PATH