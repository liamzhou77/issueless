from time import time

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from issueless.decorators import (
    access_issue_permission_required,
    assign_issue_permission_required,
    close_issue_permission_required,
    comment_and_upload_permission_required,
    delete_comment_permission_required,
    delete_file_permission_required,
    delete_issue_permission_required,
    download_file_permission_required,
    edit_issue_permission_required,
    permission_required,
    resolve_issue_permission_required,
    restore_issue_permission_required,
)
from issueless.issue import bp
from issueless.issue.helpers import (
    admin_reviewer_add_notification,
    assign_validation,
    comment_validation,
    create_presigned_url,
    create_validation,
    delete_file_in_s3,
    delete_issue_files_in_s3,
    edit_validation,
    sizeof_fmt,
    upload_file_to_s3,
)
from issueless.models import db, Comment, File, Issue, Permission, UserProject


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
        comments=issue.comments.order_by(Comment.timestamp.desc()),
        member_user_projects=user_project.project.user_projects.order_by(
            UserProject.timestamp
        ),
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
        admin_reviewer_add_notification(
            project,
            'new issue',
            {
                'avatar': current_user.avatar(),
                'fullname': current_user.fullname(),
                'projectTitle': project.title,
                'issueTitle': title,
            },
        )
        db.session.commit()

    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/edit', methods=['POST'])
@login_required
@edit_issue_permission_required
def edit(project, issue):
    """Edits an issue.

    Edits an issue's title and description. If the project's status is In Progress,
    edits the priority and assignee too.

    Produces:
        application/json
        text/html

    Args:
        project:
            in: edit_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: edit_issue_permission_required() decorator
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

        new_assignee = edit_validation(
            issue, title, description, project, priority, assignee_id
        )
        issue.priority = priority
        if issue.assignee != new_assignee:
            if issue.assignee != current_user:
                issue.assignee.add_notification(
                    'remove assignee',
                    {
                        'avatar': current_user.avatar(),
                        'fullname': current_user.fullname(),
                        'issueTitle': issue.title,
                    },
                )
            if new_assignee != current_user:
                new_assignee.add_notification(
                    'assign issue',
                    {
                        'avatar': current_user.avatar(),
                        'fullname': current_user.fullname(),
                        'projectId': project.id,
                    },
                    issue.id,
                )
            issue.assignee_id = assignee_id
    else:
        edit_validation(issue, title, description)

    issue.title = title
    issue.description = description
    db.session.commit()

    return {'success': True}


@bp.route('/<int:issue_id>/delete', methods=['POST'])
@login_required
@delete_issue_permission_required
def delete(project, issue):
    """Deletes an issue.

    Produces:
        application/json
        text/html

    Args:
        project:
            in: delete_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: delete_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.

    Responses:
        302:
            description: Redirect to project page.
        400:
            description: Bad request.
        403:
            description: Forbidden.
        404:
            description: Project or issue does not exist.
    """

    data = {
        'avatar': current_user.avatar(),
        'fullname': current_user.fullname(),
        'projectTitle': project.title,
        'issueTitle': issue.title,
    }
    if issue.creator != current_user:
        issue.creator.add_notification(
            'delete issue', data,
        )
    if issue.assignee is not None and issue.assignee != current_user:
        issue.assignee.add_notification(
            'delete issue', data,
        )

    if issue.files.first() is not None:
        delete_issue_files_in_s3(str(issue.id))
    db.session.delete(issue)
    db.session.commit()

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
            in: formData
            type: String
            description: The priority level of the issue.
        assignee_id:
            in: formData
            type: int
            description: The assignee's id.

    Responses:
        302:
            description: Redirect to project page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission.
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
        if issue.assignee != current_user:
            issue.assignee.add_notification(
                'assign issue',
                {
                    'avatar': current_user.avatar(),
                    'fullname': current_user.fullname(),
                    'projectId': project.id,
                },
                issue.id,
            )
        db.session.commit()

    return redirect(url_for('project.project', id=project.id))


@bp.route('/<int:issue_id>/restore', methods=['POST'])
@login_required
@restore_issue_permission_required
def restore(project, issue):
    """Restores a closed or resolved issue back to previous status.

    Restores a closed or resolved issue back to previous status. Restores resolved
    issue's status to In Progress. Restores closed issue's status to Open or In
    Progress based on if there is an existing assignee.

    Args:
        project:
            in: assign_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: assign_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.
        url:
            in: formData
            type: String
            description: The url to be redirected to.

    Responses:
        302:
            description: Redirect to the url page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission.
        404:
            description: Project or issue does not exist.
    """

    redirect_url = request.form.get('url')
    if issue.status == 'Closed':
        if issue.assignee is None:
            status = 'Open'
            admin_reviewer_add_notification(
                project,
                'mark open',
                {
                    'avatar': current_user.avatar(),
                    'fullname': current_user.fullname(),
                    'issueTitle': issue.title,
                },
            )
        else:
            status = 'In Progress'
            if issue.assignee != current_user:
                issue.assignee.add_notification(
                    'mark in progress',
                    {
                        'avatar': current_user.avatar(),
                        'fullname': current_user.fullname(),
                        'issueTitle': issue.title,
                        'preStatus': issue.status,
                        'projectId': project.id,
                    },
                    issue.id,
                )
        issue.closed_timestamp = None
    else:
        status = 'In Progress'
        if issue.assignee != current_user:
            issue.assignee.add_notification(
                'mark in progress',
                {
                    'avatar': current_user.avatar(),
                    'fullname': current_user.fullname(),
                    'issueTitle': issue.title,
                    'preStatus': issue.status,
                    'projectId': project.id,
                },
                issue.id,
            )
        issue.resolved_timestamp = None
    issue.status = status
    db.session.commit()
    return redirect(redirect_url)


@bp.route('/<int:issue_id>/resolve', methods=['POST'])
@login_required
@resolve_issue_permission_required
def resolve(project, issue):
    """Marks a In Progress issue as Resolved.

    Args:
        project:
            in: assign_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: assign_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.
        url:
            in: formData
            type: String
            description: The url to be redirected to.

    Responses:
        302:
            description: Redirect to the url page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission and is not the
            assignee of the issue.
        404:
            description: Project or issue does not exist.
    """

    redirect_url = request.form.get('url')

    issue.status = 'Resolved'
    issue.resolved_timestamp = time()

    issue.assignee.add_notification(
        'mark resolved',
        {
            'avatar': current_user.avatar(),
            'fullname': current_user.fullname(),
            'issueTitle': issue.title,
        },
    )

    db.session.commit()
    return redirect(redirect_url)


@bp.route('/<int:issue_id>/close', methods=['POST'])
@login_required
@close_issue_permission_required
def close(project, issue):
    """Marks an issue as closed.

    Args:
        project:
            in: close_issue_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: close_issue_permission_required() decorator
            type: Issue
            description: An Issue object whose id is the same as the id in the path.
        url:
            in: formData
            type: String
            description: The url to be redirected to.

    Responses:
        302:
            description: Redirect to the url page.
        400:
            description: Bad request.
        403:
            description: Current user does not have the permission.
        404:
            description: Project or issue does not exist.
    """

    redirect_url = request.form.get('url')
    issue.status = 'Closed'
    issue.closed_timestamp = time()

    if issue.assignee is None:
        issue.creator.add_notification(
            'mark closed',
            {
                'avatar': current_user.avatar(),
                'fullname': current_user.fullname(),
                'issueTitle': issue.title,
            },
        )
    else:
        issue.assignee.add_notification(
            'mark closed',
            {
                'avatar': current_user.avatar(),
                'fullname': current_user.fullname(),
                'issueTitle': issue.title,
            },
        )

    db.session.commit()
    return redirect(redirect_url)


@bp.route('/<int:issue_id>/upload', methods=['POST'])
@login_required
@comment_and_upload_permission_required
def upload(project, issue):
    """Uploads a new file.

    Produces:
        application/json
        text/html

    Args:
        project:
            in: comment_and_upload_permission_required() decorator
            type: Project
            description: A Project object whose id is the same as the id in the path.
        issue:
            in: comment_and_upload_permission_required() decorator
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

        uploaded_file.seek(0, 2)
        size = sizeof_fmt(uploaded_file.tell())

        uploaded_file.seek(0)
        error = upload_file_to_s3(uploaded_file, f'{issue.id}/{filename}')
        if error is not None:
            return error, 422

        file = File(filename=filename, uploader=current_user, issue=issue, size=size)
        db.session.add(file)
        db.session.commit()

    return {'filename': filename, 'size': size}


@bp.route('/<int:issue_id>/uploads/<filename>')
@login_required
@download_file_permission_required
def download(issue, file):
    """Sends the requested file to user."""
    return redirect(create_presigned_url(f'{issue.id}/{file.filename}'))


@bp.route('/<int:issue_id>/uploads/<filename>/delete', methods=['POST'])
@login_required
@delete_file_permission_required
def delete_file(issue, file):
    """Removes file form database and file system."""
    delete_file_in_s3(f'{issue.id}/{file.filename}')
    db.session.delete(file)
    db.session.commit()
    return {'success': True}


@bp.route('/<int:issue_id>/comment', methods=['POST'])
@login_required
@comment_and_upload_permission_required
def comment(project, issue):
    """Submits a new comment."""
    text = request.form.get('text')
    error = comment_validation(text)
    if error is not None:
        flash(error)
    else:
        new_comment = Comment(text=text, user=current_user, issue=issue)
        db.session.add(new_comment)
        if current_user == issue.assignee:
            admin_reviewer_add_notification(
                project,
                'new comment',
                {
                    'avatar': current_user.avatar(),
                    'fullname': current_user.fullname(),
                    'projectId': project.id,
                },
                issue.id,
            )
        else:
            issue.assignee.add_notification(
                'new comment',
                {
                    'avatar': current_user.avatar(),
                    'fullname': current_user.fullname(),
                    'projectId': project.id,
                },
                issue.id,
            )
        db.session.commit()
    return redirect(url_for('issue.issue', id=project.id, issue_id=issue.id))


@bp.route('/<int:issue_id>/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
@delete_comment_permission_required
def delete_comment(project, issue, comment):
    """Deletes a comment."""
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('issue.issue', id=project.id, issue_id=issue.id))
