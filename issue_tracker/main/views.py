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
    """Returns the dashboard page.

    Produces:
        text/html

    Responses:
        200:
            description: The dashboard html page.
    """
    user_projects = current_user.user_projects.order_by(UserProject.timestamp)
    return render_template(
        'dashboard.html', title='Dashboard', user_projects=user_projects
    )


@bp.route('/notifications')
@login_required
def notifications():
    """Returns current user's notifications.

    Produces:
        application/json

    Responses:
        200:
            description: Current user's notifications.
    """
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


# TODO: change to returning json
@bp.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
def delete_notification(id):
    """Deletes a notification.

    Args:
      - name: id
        in: path
        type: int
        description: Id of the notification to be deleted.
      - name: next
        in: query
        type: string
        description: Indicating what url to be redirected to.

    Responses:
        302:
            description: Redirect to the 'next' url.
        403:
            description: Notification does not belong to current user.
        404:
            description: Notification not found.
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
