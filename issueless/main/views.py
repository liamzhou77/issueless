from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issueless.errors.errors import ValidationError
from issueless.main import bp
from issueless.models import (
    db,
    Comment,
    Issue,
    Notification,
    Project,
    Role,
    UserProject,
)
from issueless.main.helpers import get_notification


@bp.route('/')
@login_required
def index():
    return redirect(url_for('main.dashboard'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Returns the dashboard page."""
    user_projects = current_user.user_projects.order_by(UserProject.timestamp)
    return render_template(
        'dashboard.html',
        title='Dashboard',
        user_projects=user_projects,
        project_users=[
            user_project.project.user_projects.order_by(UserProject.timestamp)
            for user_project in user_projects
        ],
        assigned_issues=current_user.assigned_issues.filter_by(
            status='In Progress', priority='High'
        )
        .order_by(Issue.timestamp)
        .union_all(
            current_user.assigned_issues.filter_by(
                status='In Progress', priority='Medium'
            ).order_by(Issue.timestamp)
        )
        .union_all(
            current_user.assigned_issues.filter_by(
                status='In Progress', priority='Low'
            ).order_by(Issue.timestamp)
        ),
        missing_review_issues=[
            issue
            for issue in Issue.query.filter(
                Issue.status == 'In Progress', Issue.assignee != current_user
            )
            .join(Issue.project)
            .join(Project.user_projects)
            .filter(UserProject.user == current_user)
            .filter(
                (UserProject.role == Role.query.filter_by(name='Admin').first())
                | (UserProject.role == Role.query.filter_by(name='Reviewer').first())
            )
            if issue.comments.first() is not None
            and issue.comments.order_by(Comment.timestamp.desc()).limit(1).first().user
            == issue.assignee
        ],
    )


@bp.route('/notifications')
@login_required
def notifications():
    """Returns current user's notifications.

    Returns current user's notifications. If path parameter 'since' is provided,
    returns notifications created after the timestamp indicating by 'since'. Otherwise,
    returns all of the user's notifications.

    Produces:
        application/json

    Args:
        since:
            in: path
            type: float
            description: A unix timestamp.

    Responses:
        200:
            description: Current user's notifications.
    """

    since = request.args.get('since', type=float)

    if since is None:
        notifications = current_user.notifications.order_by(
            Notification.timestamp.desc()
        )
    else:
        notifications = current_user.notifications.filter(
            Notification.timestamp > since
        ).order_by(Notification.timestamp)

    return {
        'success': True,
        'notifications': [notification.to_dict() for notification in notifications],
    }


@bp.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
def delete_notification(id):
    """Deletes a notification.

    Produces:
        application/json
        text/html

    Args:
        id:
            in: path
            type: int
            description: The notification's id.

    Responses:
        200:
            description: Delete successfully.
        403:
            description: Notification does not belong to current user.
        404:
            description: Notification not found.
    """

    notification = get_notification(id)

    db.session.delete(notification)
    db.session.commit()

    return {'success': True}


@bp.route('/notifications/read', methods=['POST'])
@login_required
def read_notification():
    """Marks notification as read.

    Marks notification as read. If path parameter 'id' is provided, only mark that
    notification as read. Otherwise, mark all notifications created before the
    timestamp indicating by 'before' path parameter as read.

    Produces:
        application/json
        text/html

    Args:
        id:
            in: path
            type: int
            description: The notification's id.
        before:
            in: json
            type: float
            description: A unix timestamp.

    Responses:
        200:
            description: Operation success.
        400:
            description: Bad request.
        403:
            description: Notification does not belong to current user.
        404:
            description: Notification not found.
        422:
            description: Notification has already been marked as read.
    """

    id = request.args.get('id', type=int)
    if id is not None:
        notification = get_notification(id)
        if notification.is_read:
            raise ValidationError('You have already marked this notification as read.')
        notification.is_read = True
    else:
        before = request.args.get('before', type=float)
        if before is None:
            abort(400)
        notifications = current_user.notifications.filter(
            Notification.timestamp <= before, Notification.is_read == False  # noqa
        )
        for notification in notifications:
            notification.is_read = True

    db.session.commit()
    return {'success': True}
