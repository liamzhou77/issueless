from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from issue_tracker.dashboard import views
