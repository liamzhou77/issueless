from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

from issue_tracker.auth import views
