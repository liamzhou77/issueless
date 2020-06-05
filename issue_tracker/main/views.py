"""All views for main blueprint.

  Typical usage example:

  from main import views
"""

from flask import abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.main import bp
from issue_tracker.models import db, UserProject, Notification
from werkzeug.urls import url_parse


@bp.route('/')
@login_required
def index():
    """Redirects to dashboard view."""
    return redirect(url_for('main.dashboard'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard template."""
    user_projects = current_user.user_projects.order_by(UserProject.timestamp)
    return render_template(
        'dashboard.html', title='Dashboard', user_projects=user_projects
    )


@bp.route('/notifications')
@login_required
def notifications():
    """Returns notifications in json."""
    notifications = current_user.notifications.order_by(
        Notification.timestamp.desc()
    ).all()
    return jsonify(
        [
            {
                'notificationId': n.id,
                'name': n.name,
                'targetId': n.target_id,
                'data': n.get_data(),
                'timestamp': n.timestamp,
            }
            for n in notifications
        ]
    )


@bp.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
def delete_notification(id):
    """Deletes a notification.

    Args:
        id: A notification's id.
        next: A url parameter indicating what url to be redirected to.

    Aborts:
        403 Forbidden: A status code aborted if the notification does not belong to
            current user.
        404 Not Found: A status code aborted if notification does not exist.

    Returns:
        Redirect to the 'next' url.
    """

    notification = Notification.query.get_or_404(id)

    if notification.user != current_user:
        abort(403)

    db.session.delete(notification)
    db.session.commit()

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)
