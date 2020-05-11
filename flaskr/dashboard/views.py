from flask import render_template
from flask_login import login_required

from flaskr.dashboard import bp


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('base.html')
