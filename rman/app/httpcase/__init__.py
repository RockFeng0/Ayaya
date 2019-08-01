from flask import Blueprint

httpcase = Blueprint('httpcase', __name__)
from .views import testset, testapi, testsuite
