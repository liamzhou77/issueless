from issueless.errors.errors import ValidationError
from issueless.models import User


def create_validation(title, description):
    return _title_description_validation(title, description)


def edit_validation(
    issue, title, description, project=None, priority=None, assignee_id=None
):
    if issue.status != 'Open' and issue.status != 'In Progress':
        raise ValidationError('You can only edit an open or in progress issue.')

    error = _title_description_validation(title, description)
    if error is not None:
        raise ValidationError(error)

    if issue.status == 'Open':
        if issue.title == title and issue.description == description:
            raise ValidationError('No changes have been made.')
    else:
        if priority != 'High' and priority != 'Medium' and priority != 'Low':
            raise ValidationError('Please provide a valid priority level.')

        assignee = User.query.get_or_404(assignee_id)
        if assignee not in project.users:
            raise ValidationError('The user you chose is not a member of the project.')

        if (
            issue.title == title
            and issue.description == description
            and priority == issue.priority
            and assignee == issue.assignee
        ):
            raise ValidationError('No changes have been made.')


def _title_description_validation(title, description):
    error = None
    if not title:
        error = "Please provide the issue's title."
    if len(title) > 80:
        error = "Issue's title can not be more than 80 character."
    if not description:
        error = "Please provide the issue's description."
    if len(description) > 200:
        error = "Issue's description can not be more than 200 characters."
    return error


def assign_validation(project, issue, priority, assignee_id):
    error = None

    if priority != 'High' and priority != 'Medium' and priority != 'Low':
        error = 'Please provide a valid priority level.'

    assignee = User.query.get_or_404(assignee_id)
    if assignee not in project.users:
        error = 'The user you chose is not a member of the project.'
    if issue.assignee is not None:
        error = f'The issue has already been assigned to {issue.assignee.fullname()}.'

    return error


def close_validation(issue):
    error = None
    if issue.status == 'Resolved':
        error = 'The issue has already been resolved.'
    elif issue.status == 'Closed':
        error = 'The issue has already been marked as closed.'
    return error
