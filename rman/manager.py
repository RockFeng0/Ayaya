#! python3
# -*- encoding: utf-8 -*-

from rman.app import create_app, db
from flask_migrate import Migrate

APP = create_app()

migrate = Migrate(APP, db)


if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=5000, debug=True)
