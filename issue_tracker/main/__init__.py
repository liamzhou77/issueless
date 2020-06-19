from flask import Blueprint

bp = Blueprint('main', __name__)

from issue_tracker.main import views
