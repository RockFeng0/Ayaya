from flask import Blueprint

case = Blueprint('case', __name__)
from . import views
