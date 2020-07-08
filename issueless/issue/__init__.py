from flask import Blueprint

bp = Blueprint('issue', __name__, url_prefix='/projects/<int:id>/issues')

from issueless.issue import views
