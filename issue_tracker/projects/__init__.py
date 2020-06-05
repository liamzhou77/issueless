"""A blueprint for projects views.

  Typical usage example:

  app.register_blueprint(projects.bp)
"""

from flask import Blueprint

bp = Blueprint('projects', __name__, url_prefix='/projects')

from issue_tracker.projects import views
