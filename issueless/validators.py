from flask_login import current_user

from issueless.errors.errors import ValidationError
from issueless.models import Role, User


def create_project_validation(title, description):
    """Checks if a project's title and description are valid before creation.

    Args:
        title: A project's title.
        description: A project's description.

    Returns:
        An error message, None if there is no error.
    """

    error = _project_validation(title, description)
    if error is None and current_user.user_projects.count() >= 4:
        error = 'You can only create or join 4 or less projects. Please delete or quit '
        'one existing project before you add any more.'
    return error


def update_project_validation(project, title, description):
    """Checks if a project's title and description are valid before update.

    Args:
        project: A project to be validated.
        title: A project's title.
        description: A project's description.

    Raises:
        ValidationError:
            description: Validation error.
    """

    error = _project_validation(title, description)
    if error is not None:
        raise ValidationError(error)
    elif project.title == title and project.description == description:
        raise ValidationError('No changes have been made.')


def _project_validation(title, description):
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


def invititation_validation(project, username, role_name):
    """Checks if an invitation is valid.

    Args:
        project: The project to be invited to.
        username: The invited user's username.
        role_name: The role's name to be assigned.

    Returns:
        The user to be invited.

    Raises:
        ValidationError:
            description: Validation error.
    """

    user = User.query.filter_by(username=username).first()
    role = Role.query.filter_by(name=role_name).first()

    error = None
    if user is None:
        error = 'Please provide a valid username.'
    elif role is None or role.name == 'Admin':
        error = 'Please provide a valid role.'
    elif user == current_user:
        error = 'You can not invite yourself to your project.'
    elif user in project.users:
        error = 'User is already a member of the project.'
    elif project.user_projects.count() >= 30:
        error = 'You can only have 30 or less members in one project.'
    if error is not None:
        raise ValidationError(error)

    return user


def join_project_validation(project):
    """Checks if the request to join a project is valid.

    Args:
        project: The project to be joined in.

    Raises:
        ValidationError:
            description: Validation error.
    """

    if current_user.user_projects.count() >= 4:
        raise ValidationError(
            'You can only create or join 4 or less projects. Please delete or quit '
            'one existing project before you add any more.'
        )
    elif project.user_projects.count() >= 30:
        raise ValidationError(
            'Failed to join the project. The project does not have any remaining '
            'spot.'
        )


def delete_member_validation(project, user):
    """Checks if the request to delete a member is valid.

    Args:
        project: The project object.
        user: The user to be removed.

    Returns:
        The UserProject to be deleted.

    Raises:
        ValidationError:
            description: Validation error.
    """

    user_project = project.user_projects.filter_by(user=user).first()
    if user_project is None:
        raise ValidationError('The user to be deleted is not a member of the project.')
    if user == current_user:
        raise ValidationError('You can not remove yourself from the project.')
    return user_project
