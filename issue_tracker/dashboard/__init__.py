from flask import Blueprint

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

from issue_tracker.dashboard import views
