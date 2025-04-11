#! python3
# -*- encoding: utf-8 -*-

from flask import send_file
from rman.app import create_app, celery, db
from flask_migrate import Migrate

APP = create_app()

migrate = Migrate(APP, db)
celery.set_path()

@APP.route('/', methods = ["GET"])
def index():
    return "hello"
    # return send_file('index.html')


if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=5000, debug=True)