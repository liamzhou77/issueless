from flask import Blueprint

bp = Blueprint('errors', __name__, url_prefix='/errors')

from issueless.errors import handlers
