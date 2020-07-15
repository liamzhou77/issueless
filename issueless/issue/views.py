import shutil
import os

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from issueless.decorators import (
    access_issue_permission_required,
    assign_issue_permission_required,
    manage_issue_permission_required,
    permission_required,
    upload_file_permission_required,
)
from issueless.issue import bp
from issueless.issue.helpers import (
    assign_validation,
    close_validation,
    create_validation,
    edit_validation,
    sizeof_fmt,
)
from issueless.models import db, File, Issue, Permission


@bp.route('/<int:issue_id>')
@login_required
@access_issue_permission_required
def issue(user_project, issue):
    """Renders the issue page."""
    return render_template(
        'issue.html',
        title=issue.title,
        user_project=user_project,
        issue=issue,
        files=issue.files.order_by(File.timestamp),
    )


@bp.route('/create', methods=['POST'])
@login_required
@permission_required(Permission.READ_PROJECT)
def create(user_project):
    """Creates a new issue.

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
            and project_id is the same as the query parameter - id.
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
        403:
            description: Forbidden.
        404:
            description: Project not found.
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
        os.makedirs(os.path.join(current_app.config['UPLOAD_PATH'], str(new_issue.id)))

    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/edit', methods=['POST'])
@login_required
@manage_issue_permission_required
def edit(project, issue):
    """Edits an issue.

    Edits an issue's title and description. If the project's status is In Progress,
    edits the priority and assignee too.

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
        title:
            in: json
            type: string
            description: The issue's new title.
        description:
            in: json
            type: string
            description: The issue's new description.
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
            description: Edit successfully.
        400:
            description: Bad request.
        403:
            description: Forbidden.
        404:
            description: Project or issue does not exist.
        422:
            description: Unprocessable.
    """

    body = request.get_json()
    title = body.get('title')
    description = body.get('description')
    if None in (title, description):
        abort(400)

    if issue.status == 'In Progress':
        priority = body.get('priority')
        assignee_id = body.get('assignee_id')
        if None in (priority, assignee_id):
            abort(400)

        edit_validation(issue, title, description, project, priority, assignee_id)
        issue.priority = priority
        issue.assignee_id = assignee_id
    else:
        edit_validation(issue, title, description)

    issue.title = title
    issue.description = description
    db.session.commit()

    return {'success': True}


@bp.route('/<int:issue_id>/delete', methods=['POST'])
@login_required
@manage_issue_permission_required
def delete(project, issue):
    """Deletes an issue.

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

    Responses:
        302:
            description: Redirect to project page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    db.session.delete(issue)
    db.session.commit()
    shutil.rmtree(
        os.path.join(current_app.config['UPLOAD_PATH'], str(issue.id)),
        ignore_errors=True,
    )
    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/assign', methods=['POST'])
@login_required
@assign_issue_permission_required
def assign(project, issue):
    """Assigns an issue.

    Args:
        project:
            in: assign_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: assign_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.
        priority:
            in: json
            type: formData
            description: The priority level of the issue.
        assignee_id:
            in: json
            type: formData
            description: The assignee's id.

    Responses:
        302:
            description: Redirect to project page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    priority = request.form.get('priority')
    assignee_id = request.form.get('assignee_id')

    error = assign_validation(project, issue, priority, assignee_id)

    if error is not None:
        flash(error)
    else:
        issue.priority = priority
        issue.status = 'In Progress'
        issue.assignee_id = assignee_id
        db.session.commit()

    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/close', methods=['POST'])
@login_required
@manage_issue_permission_required
def close(project, issue):
    """Marks an issue as closed.

    Args:
        project:
            in: manage_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: manage_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.

    Responses:
        302:
            description: Redirect to project page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    error = close_validation(issue)

    if error is not None:
        flash(error)
    else:
        issue.status = 'Closed'
        db.session.commit()

    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/upload', methods=['POST'])
@login_required
@upload_file_permission_required
def upload(project, issue):
    """Uploads a new file.

    Produces:
        application/json
        text/html

    Args:
        project:
            in: upload_file_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: upload_file_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.

    Responses:
        200:
            description: Upload successfully.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission and is not the
                creator of the issue.
        404:
            description: Project or issue does not exist.
    """

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        if issue.files.filter_by(filename=filename).first() is not None:
            return 'You can not upload duplicate files.', 422

        uploaded_file.save(
            os.path.join(current_app.config['UPLOAD_PATH'], str(issue.id), filename)
        )

        size = sizeof_fmt(
            os.path.getsize(
                os.path.join(current_app.config['UPLOAD_PATH'], str(issue.id), filename)
            )
        )
        file = File(filename=filename, uploader=current_user, issue=issue, size=size)
        db.session.add(file)
        db.session.commit()

    return {'filename': filename, 'size': size}


@bp.route('/<int:issue_id>/uploads')
@login_required
@access_issue_permission_required
def download(project, issue):
    """Sends the requested file to user."""
    filename = request.args.get('filename')
    if filename is None:
        abort(400)
    if issue.files.filter_by(filename=filename).first() is None:
        abort(404)
    return send_from_directory(
        os.path.join('..', current_app.config['UPLOAD_PATH'], str(issue.id)), filename,
    )


@bp.route('/<int:issue_id>/uploads/delete', methods=['POST'])
@login_required
@upload_file_permission_required
def delete_file(project, issue):
    """Removes file form database and file system."""
    filename = request.args.get('filename')
    if filename is None:
        abort(400)

    file = issue.files.filter_by(filename=filename).first()
    if file is None:
        abort(404)
    db.session.delete(file)
    db.session.commit()
    os.remove(os.path.join(current_app.config['UPLOAD_PATH'], str(issue.id), filename))
    return {'success': True}
