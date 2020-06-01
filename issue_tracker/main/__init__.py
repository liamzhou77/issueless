"""A blueprint for main views.

  Typical usage example:

  app.register_blueprint(main.bp)
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from issue_tracker.main import views
