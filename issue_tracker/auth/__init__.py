"""A blueprint for authorization.

  Typical usage example:

  app.register_blueprint(auth.bp)
"""

from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

from issue_tracker.auth import views
