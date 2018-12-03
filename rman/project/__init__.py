from flask import Blueprint

project = Blueprint('project', __name__, template_folder="templates")
from .views import *
