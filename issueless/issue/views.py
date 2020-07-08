from flask import abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from issueless.decorators import (
    assign_issue_permission_required,
    manage_issue_permission_required,
    permission_required,
)
from issueless.issue import bp
from issueless.issue.helpers import (
    assign_validation,
    create_validation,
    edit_validation,
)
from issueless.models import db, Issue, Permission


@bp.route('/create', methods=['POST'])
@login_required
@permission_required(Permission.READ_PROJECT)
def create(user_project):
    """Creates a new issue.

    Args:
        title：
            in: formData
            type: string
            description: The new issue's title.
        description：
            in: formData
            type: string
            description: The new issue's description.

    Responses:
        302:
            description: Redirect to project page.
    """

    title = request.form.get('title')
    description = request.form.get('description')

    project = user_project.project
    error = create_validation(title, description)
    if error is not None:
        flash(error)
    else:
        new_issue = Issue(
            title=title, description=description, creator=current_user, project=project,
        )
        db.session.add(new_issue)
        db.session.commit()

    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/edit', methods=['POST'])
@login_required
@manage_issue_permission_required
def edit(issue):
    """Edits an issue.

    Produces:
        application/json
        text/html

    Args:
        issue:
            in: manage_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.
        title:
            in: json
            type: string
            description: The issue's new title.
        description:
            in: json
            type: string
            description: The issue's new description.


    Responses:
        200:
            Edit successfully.
        400:
            Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    body = request.get_json()
    title = body.get('title')
    description = body.get('description')
    if None in (title, description):
        abort(400)

    edit_validation(issue, title, description)

    issue.title = title
    issue.description = description
    db.session.commit()

    return {'success': True}


@bp.route('/<int:issue_id>/delete', methods=['POST'])
@login_required
@manage_issue_permission_required
def delete(issue):
    """Deletes an issue.

    Produces:
        application/json
        text/html

    Args:
        issue:
            in: manage_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.

    Responses:
        200:
            Delete successfully.
        400:
            Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    db.session.delete(issue)
    db.session.commit()
    return {'success': True}


@bp.route('/<int:issue_id>/assign', methods=['POST'])
@login_required
@assign_issue_permission_required
def assign(project, issue):
    """Assigns an issue.

    Produces:
        application/json
        text/html

    Args:
        project:
            in: manage_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: manage_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.
        priority:
            in: json
            type: String
            description: The priority level of the issue.
        assignee_id:
            in: json
            type: String
            description: The assignee's id.

    Responses:
        200:
            Assign successfully.
        400:
            Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    body = request.get_json()
    priority = body.get('priority')
    assignee_id = body.get('assignee_id')
    if None in (priority, assignee_id):
        abort(400)

    assign_validation(project, issue, priority, assignee_id)

    issue.priority = priority
    issue.status = 'In Progress'
    issue.assignee_id = assignee_id
    db.session.commit()

    return {'success': True}
