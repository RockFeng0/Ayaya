from flask import Blueprint

httptest = Blueprint('httptest', __name__)
from . import views
