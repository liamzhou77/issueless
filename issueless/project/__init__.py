from flask import Blueprint

bp = Blueprint('project', __name__, url_prefix='/projects')

from issueless.project import views
