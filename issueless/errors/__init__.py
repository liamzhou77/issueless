from flask import Blueprint

bp = Blueprint('errors', __name__)

from issueless.errors import handlers
