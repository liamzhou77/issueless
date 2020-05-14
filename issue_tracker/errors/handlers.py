from flask import render_template

from issue_tracker.errors import bp
from issue_tracker.models import db


@bp.app_errorhandler(401)
def unauthorized(error):
    return render_template('errors/401.html'), 401


@bp.app_errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
