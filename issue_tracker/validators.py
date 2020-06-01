"""Defines all validators.

  Typical usage example:

  error = project_validation('Issue Tracker', 'A web app')
  if error:
      flash(error)
      return redirect(...)
"""


def project_validation(title, description):
    """Checks if a project's title and description are valid.

    Args:
        title: A project's title.
        description: A project's description.

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
