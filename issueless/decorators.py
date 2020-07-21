"""Defines all decorators.

Typical usage example:

@permission_required(Permission.MANAGE_PROJECT)
def create:
"""

from functools import wraps

from flask import abort
from flask_login import current_user

from issueless.models import Comment, File, Issue, Permission, Project


def _get_user_project(id):
    project = Project.query.get_or_404(id)
    user_project = current_user.user_projects.filter_by(project=project).first()
    if user_project is None:
        abort(403)
    return user_project


def _get_issue(project_id, issue_id):
    user_project = _get_user_project(project_id)
    issue = Issue.query.get_or_404(issue_id)
    if user_project.project != issue.project:
        abort(400)
    return (user_project, issue)


def _get_file(project_id, issue_id, filename):
    user_project, issue = _get_issue(project_id, issue_id)
    file = File.query.filter_by(filename=filename).first()
    if file is None:
        abort(404)
    if file.issue != issue:
        abort(400)
    return (user_project, issue, file)


def permission_required(permission):
    """Checks user's permission to access certain project.

    Args:
        permission: The permission name to be checked for.

    Returns:
        A decorator that adds functionality to check for permission.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(id, *args, **kwargs):
            """
            Args:
                id: A project's id to be checked for.
            """

            user_project = _get_user_project(id)
            if not user_project.can(permission):
                abort(403)

            return f(user_project, *args, **kwargs)

        return wrapper

    return decorator


def access_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)

        if issue.assignee is None:
            abort(400)
        if not user_project.can(Permission.READ_PROJECT):
            abort(403)

        return f(user_project, issue, *args, **kwargs)

    return wrapper


def edit_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)

        if issue.status != 'Open' and issue.status != 'In Progress':
            abort(400)

        if (
            issue.status == 'Open'
            and not user_project.can(Permission.MANAGE_ISSUES)
            and issue.creator != current_user
        ) or (
            issue.status == 'In Progress'
            and not user_project.can(Permission.MANAGE_ISSUES)
        ):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def delete_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)

        if (
            issue.status == 'Open'
            and not user_project.can(Permission.MANAGE_ISSUES)
            and issue.creator != current_user
        ) or (
            issue.status != 'Open' and not user_project.can(Permission.MANAGE_ISSUES)
        ):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def assign_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)
        if issue.status != 'Open':
            abort(400)
        if not user_project.can(Permission.MANAGE_ISSUES):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def close_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)
        if issue.status != 'Open' and issue.status != 'In Progress':
            abort(400)
        if not user_project.can(Permission.MANAGE_ISSUES):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def resolve_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)
        if issue.status != 'In Progress':
            abort(400)
        if issue.assignee == current_user or not user_project.can(
            Permission.MANAGE_ISSUES
        ):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def restore_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)
        if issue.status != 'Closed' and issue.status != 'Resolved':
            abort(400)
        if not user_project.can(Permission.MANAGE_ISSUES):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def download_file_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, filename, *args, **kwargs):
        user_project, issue, file = _get_file(id, issue_id, filename)
        if issue.assignee is None:
            abort(400)
        if not user_project.can(Permission.READ_PROJECT):
            abort(403)

        return f(issue, file, *args, **kwargs)

    return wrapper


def delete_file_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, filename, *args, **kwargs):
        user_project, issue, file = _get_file(id, issue_id, filename)
        if issue.assignee is None:
            abort(400)
        if (
            not user_project.can(Permission.MANAGE_ISSUES)
            and file.uploader != current_user
        ):
            abort(403)

        return f(issue, file, *args, **kwargs)

    return wrapper


def comment_and_upload_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)

        if issue.status != 'In Progress':
            abort(400)

        if (
            not user_project.can(Permission.MANAGE_ISSUES)
            and issue.creator != current_user
            and issue.assignee != current_user
        ):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper


def delete_comment_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, comment_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)
        comment = Comment.query.get_or_404(comment_id)
        if comment.issue != issue:
            abort(400)
        if (
            not user_project.can(Permission.MANAGE_ISSUES)
            and comment.user != current_user
        ):
            abort(403)

        return f(user_project.project, issue, comment, *args, **kwargs)

    return wrapper
