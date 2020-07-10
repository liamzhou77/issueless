"""Defines all decorators.

Typical usage example:

@permission_required(Permission.MANAGE_PROJECT)
def create:
"""

from functools import wraps

from flask import abort
from flask_login import current_user

from issueless.models import Issue, Permission, Project


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


def manage_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)

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


def assign_issue_permission_required(f):
    @wraps(f)
    def wrapper(id, issue_id, *args, **kwargs):
        user_project, issue = _get_issue(id, issue_id)
        if not user_project.can(Permission.MANAGE_ISSUES):
            abort(403)

        return f(user_project.project, issue, *args, **kwargs)

    return wrapper
