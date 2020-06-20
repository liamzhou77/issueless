from flask import render_template

from issueless.errors import bp
from issueless.errors.errors import ValidationError
from issueless.models import db


@bp.app_errorhandler(400)
def bad_request(error):
    return render_template('/errors/400.html'), 400


@bp.app_errorhandler(401)
def unauthorized(error):
    return render_template('/errors/401.html'), 401


@bp.app_errorhandler(403)
def forbidden(error):
    return render_template('/errors/403.html'), 403


@bp.app_errorhandler(404)
def not_found(error):
    return render_template('/errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('/errors/500.html'), 500


@bp.app_errorhandler(ValidationError)
def form_validation_error(error):
    return {'success': False, 'error': error.error}, 422
