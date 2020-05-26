"""A blueprint for error handlers.

  Typical usage example:

  app.register_blueprint(errors.bp)
"""

from flask import Blueprint

bp = Blueprint('errors', __name__)

from issue_tracker.errors import handlers
