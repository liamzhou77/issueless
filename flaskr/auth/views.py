from flask import current_app, request, url_for

from flaskr.auth import bp
from flaskr.oauth import configure_oauth


@bp.route('/callback')
def callback():
    pass


@bp.route('/login')
def login():
    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)
    return auth0.authorize_redirect(
        # Generate the callback url
        redirect_uri=request.url_root
        + url_for('auth.callback')[1:]
    )
