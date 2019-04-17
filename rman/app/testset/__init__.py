from flask import Blueprint

testset = Blueprint('testset', __name__)
from . import views
