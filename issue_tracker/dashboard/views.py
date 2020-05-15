from flask import render_template
from flask_login import current_user, login_required

from issue_tracker.dashboard import bp


@bp.route('/dashboard')
@login_required
def dashboard():
    projects = current_user.projects.all()
    return render_template('dashboard.html', title='Dashboard', projects=projects)
