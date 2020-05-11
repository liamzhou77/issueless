from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from flaskr.dashboard import views
