"""Defines all decorators.

  Typical usage example:

  @permission_required(Permission.UPDATE_PROJECT)
  def update:
"""

from functools import wraps

from flask import abort

from flask_login import current_user


def permission_required(permission):
    """Checks user's permission to access certain project.

    Args:
        permission: The permission name to be checked for.

    Returns:
        A decorator that adds functionality to check for permission.

    Aborts:
        403 Forbidden: A status code aborted if current user does not have the
            permission.
        404 Not Found: A status code aborted if current user doesn't have the target
            project.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(id, *args, **kwargs):
            """
            Args:
                id: The target project's id to be checked for.
            """

            user_project = current_user.user_projects.filter_by(project_id=id).first()

            if not user_project:
                abort(404)
            if not user_project.can(permission):
                abort(403)

            return f(user_project, *args, **kwargs)

        return wrapper

    return decorator
