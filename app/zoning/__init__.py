from flask import Blueprint

zoning = Blueprint('zoning', __name__)

from . import views
