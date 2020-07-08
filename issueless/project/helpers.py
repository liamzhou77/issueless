from flask_login import current_user

from issueless.errors.errors import ValidationError
from issueless.models import Role, User


def create_validation(title, description):
    """Checks if a project's title and description are valid before creation.

    Args:
        title: A project's title.
        description: A project's description.

    Returns:
        An error message, None if there is no error.
    """

    error = title_description_validation(title, description)
    if error is None and current_user.user_projects.count() >= 8:
        error = (
            'You can only have 8 or less projects. Please leave one existing '
            'project before you add any more.'
        )
    return error


def edit_validation(project, title, description):
    """Checks if a project's title and description are valid before edit.

    Args:
        project: A project to be validated.
        title: A project's title.
        description: A project's description.

    Raises:
        ValidationError:
            description: Validation error.
    """

    error = title_description_validation(title, description)
    if error is not None:
        raise ValidationError(error)
    elif project.title == title and project.description == description:
        raise ValidationError('No changes have been made.')


def title_description_validation(title, description):
    error = None
    if not title:
        error = "Please provide the project's title."
    elif len(title) > 80:
        error = "Project's title can not be more than 80 character."
    elif not description:
        error = "Please provide the project's description."
    elif len(description) > 200:
        error = "Project's description can not be more than 200 characters."
    return error


def invite_validation(project, target, role_name):
    """Checks if an invitation is valid.

    Args:
        project: The project to be invited to.
        target: The invited user's username or email address.
        role_name: The role's name to be assigned.

    Returns:
        The user to be invited.

    Raises:
        ValidationError:
            description: Validation error.
    """

    user = User.query.filter((User.username == target) | (User.email == target)).first()
    role = Role.query.filter_by(name=role_name).first()

    if role is None or role.name == 'Admin':
        raise ValidationError('Please provide a valid role.')

    if user is not None:
        error = None
        if user == current_user:
            error = 'You can not invite yourself to your project.'
        elif user in project.users:
            error = 'User is already a member of the project.'
        elif project.user_projects.count() >= 30:
            error = 'You can only have 30 or less members in one project.'
        if error is not None:
            raise ValidationError(error)

    return user


def join_validation(project):
    """Checks if the request to join a project is valid.

    Args:
        project: The project to be joined in.

    Raises:
        ValidationError:
            description: Validation error.
    """

    if project is None:
        raise ValidationError('The project has been removed.')
    if current_user.user_projects.count() >= 8:
        raise ValidationError(
            'You can only have 8 or less projects. Please leave one existing project '
            'before you add any more.'
        )
    elif project.user_projects.count() >= 30:
        raise ValidationError('The project does not have any remaining spot.')


def remove_member_validation(project, user):
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

    return _member_validation(
        project,
        user,
        'The user to be removed is not a member of the project.',
        'You can not remove yourself from the project.',
    )


def change_role_validation(project, user):
    return _member_validation(
        project,
        user,
        'User is not a member of the project.',
        'You can not assign yourself a new role.',
    )


def _member_validation(project, user, not_member_msg, is_current_user_msg):
    user_project = project.user_projects.filter_by(user=user).first()
    if user_project is None:
        raise ValidationError(not_member_msg)
    if user == current_user:
        raise ValidationError(is_current_user_msg)
    return user_project
