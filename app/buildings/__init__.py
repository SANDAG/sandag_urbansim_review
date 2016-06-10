from flask import Blueprint

buildings = Blueprint('buildings', __name__)

from . import views
