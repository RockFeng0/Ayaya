from flask import Blueprint

rm_task = Blueprint('rm_task', __name__)
from . import views
