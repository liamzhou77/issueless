"""Defines all decorators.

  Typical usage example:

  @permission_required(Permission.MANAGE_PROJECT)
  def update:
"""

from functools import wraps

from flask import abort
from flask_login import current_user

from issue_tracker.models import Project


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

            Aborts:
                403 Forbidden: A status code aborted if current user is not a member of
                    the project or does not have the permission.
                404 Not Found: A status code aborted if project does not exist.
            """

            project = Project.query.get_or_404(id)

            user_project = current_user.user_projects.filter_by(project=project).first()
            if not user_project or not user_project.can(permission):
                abort(403)

            return f(user_project, *args, **kwargs)

        return wrapper

    return decorator
