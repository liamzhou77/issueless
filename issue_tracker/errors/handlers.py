"""All handlers for errors blueprint.

  Typical usage example:

  from errors import views
"""


from flask import jsonify, render_template

from issue_tracker.errors import bp
from issue_tracker.errors.errors import FormValidationError
from issue_tracker.models import db


@bp.app_errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(FormValidationError)
def form_validation_error(error):
    return jsonify({'success': False, 'message': error.message}), 422
