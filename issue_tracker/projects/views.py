from flask import flash, redirect, request, url_for
from flask_login import current_user, login_required

from issue_tracker.decorators import permission_required
from issue_tracker.models import Permission, Project
from issue_tracker.projects import bp


@bp.route('/create', methods=['POST'])
@login_required
def create():
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
    error = _project_validation(title, description)
    if error:
        flash(error)
        return redirect(url_for('index'))

    project = Project(title=title, description=description)
    current_user.insert_project(project, 'Admin')
    return redirect(url_for('index'))


@bp.route('/<int:id>/update', methods=['POST'])
@login_required
@permission_required(Permission.UPDATE_PROJECT)
def update(project):
    """Updates a project's information.

    Args:
        project: A project object returned from permission_required decorator, whose id
        is the same as the one in the url.

    Returns:
        Redirect to dashboard view.
    """
    title = request.form.get('title')
    description = request.form.get('description')
    error = _project_validation(title, description)
    if error:
        flash(error)
        return redirect(url_for('index'))

    project.title = title
    project.description = description
    project.update()
    return redirect(url_for('index'))


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.DELETE_PROJECT)
def delete(project):
    """Deletes a project.

    Args:
        project: A project object returned from permission_required decorator, whose id
        is the same as the one in the url.

    Returns:
        Redirect to dashboard view.
    """

    project.delete()
    return redirect(url_for('index'))


def _project_validation(title, description):
    """Checks if a project's title and description are valid.

    Returns:
        An error message, None if there is no error.
    """
    error = None
    if not title:
        error = "Project's title is required."
    elif len(title) > 50:
        error = "Project's title can not be more than 50 character."
    elif not description:
        error = "Project's description is required."
    elif len(description) > 200:
        error = "Project's description can not be more than 200 characters."
    return error
