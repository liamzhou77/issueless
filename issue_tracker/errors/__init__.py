from flask import Blueprint

bp = Blueprint('errors', __name__)

from issue_tracker.errors import handlers
