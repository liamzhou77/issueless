from flask import Blueprint

bp = Blueprint('project', __name__, url_prefix='/projects')

from issue_tracker.project import views
