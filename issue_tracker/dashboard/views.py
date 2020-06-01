"""All views for dashboard blueprint.

  Typical usage example:

  from dashboard import views
"""

from flask import render_template
from flask_login import current_user, login_required

from issue_tracker.dashboard import bp


@bp.route('/')
@login_required
def index():
    """Renders the dashboard template."""
    user_projects = current_user.user_projects
    return render_template(
        'dashboard/index.html', title='Dashboard', user_projects=user_projects
    )
