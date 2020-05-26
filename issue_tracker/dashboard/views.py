"""All views for dashboard.

  Typical usage example:

  from dashboard import views
"""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.dashboard import bp
from issue_tracker.decorators import permission_required
from issue_tracker.models import Permission, Project


@bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard template."""
    user_projects = current_user.user_projects
    return render_template(
        'dashboard.html', title='Dashboard', user_projects=user_projects
    )


@bp.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    """Creates a new project.

    Form Data:
        title: A project's title.
        description: A project's description.

    Returns:
        Redirect to dashboard view.
    """

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

    project = Project(title=title, description=description)
    current_user.insert_project(project, 'Admin')
    return redirect(url_for('index'))


@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.DELETE_PROJECT)
def delete_project(id):
    """Deletes a project.

    Args:
        id: The id of the project to be deleted, passed from a section of url.

    Returns:
        Redirect to dashboard view.
    """

    project = Project.query.get(id)
    project.delete()
    return redirect(url_for('index'))
