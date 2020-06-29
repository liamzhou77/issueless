from flask import abort
from flask_login import current_user

from issueless.models import Notification


def get_notification(id):
    notification = Notification.query.get_or_404(id)
    if notification.user != current_user:
        abort(403)
    return notification
