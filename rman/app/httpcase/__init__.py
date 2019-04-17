from flask import Blueprint

httpcase = Blueprint('httpcase', __name__)
from . import views
