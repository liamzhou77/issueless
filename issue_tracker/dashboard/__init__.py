"""A blueprint for dashboard.

  Typical usage example:

  app.register_blueprint(dashboard.bp)
"""

from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from issue_tracker.dashboard import views
