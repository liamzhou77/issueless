from flask import Blueprint

bp = Blueprint('main', __name__)

from issueless.main import views
