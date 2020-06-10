"""Defines all validators.

  Typical usage example:

  error = project_validation('Issue Tracker', 'A web app')
  if error:
      flash(error)
      return redirect(...)
"""


from issue_tracker.errors.errors import FormValidationError


def create_project_validation(title, description):
    """Checks if a project's title and description are valid before creation.

    Args:
        title: A project's title.
        description: A project's description.

    Returns:
        An error message, None if there is no error.
    """

    error = None
    if not title:
        error = "Please provide your project's title."
    elif len(title) > 50:
        error = "Project's title can not be more than 50 character."
    elif not description:
        error = "Please provide your project's description."
    elif len(description) > 200:
        error = "Project's description can not be more than 200 characters."
    return error


def update_project_validation(project, title, description):
    """Checks if a project's title and description are valid before update.

    Args:
        project: A project to be validated.
        title: A project's title.
        description: A project's description.

    Raises:
        FormValidationError: Form field is invalid.
    """

    message = create_project_validation(title, description)
    if project.title == title and project.description == description:
        message = "No changes have been made."

    if message:
        raise FormValidationError(message)
