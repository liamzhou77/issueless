from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.dashboard import bp
from issue_tracker.models import Project


@bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard template."""
    user_projects = current_user.user_projects
    return render_template(
        'dashboard.html', title='Dashboard', user_projects=user_projects
    )


@bp.route('/projects', methods=['POST'])
@login_required
def projects():
    """Creates a new project."""
    # Each user can only create 4 projects at most. If the limit has already been
    # arrived, redirect user to dashboard with an error message
    project_count = current_user.user_projects.count()
    if project_count == 4:
        flash(
            'You can not add any more projects, you can only create 4 or less projects.'
            'Please delete one existing project before you add any more.'
        )
        return redirect(url_for('index'))

    title = request.form.get('title')
    description = request.form.get('description')
    # add verification for post data in server side just for safety
    error = None
    if not title:
        error = "Project's title is required."
    elif len(title) > 50:
        error = "Project's title can not be more than 50 character."
    elif not description:
        error = "Project's description is required."
    elif len(description) > 200:
        error = "Project's description can not be more than 200 characters."
    if error:
        flash(error)
        return redirect(url_for('index'))

    project = Project(title, description)
    current_user.insert_project(project, 'Admin')
    return redirect(url_for('index'))
