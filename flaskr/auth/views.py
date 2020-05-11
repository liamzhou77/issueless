from flask import abort, current_app, redirect, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from flaskr.auth import bp
from flaskr.models import User
from flaskr.oauth import configure_oauth
from six.moves.urllib.parse import urlencode


@bp.route('/callback')
def callback():
    """Logs users in after they are authenticated by Auth0."""
    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)

    # Hard coding callback route in browser would result in various exceptions. In this
    # case an Unauthorized error with 401 status code would be more appropriate,
    # because only Auth0 is authorized to access this callback route.
    try:
        auth0.authorize_access_token()
    except Exception:
        abort(401)

    rsp = auth0.get('userinfo')
    userinfo = rsp.json()

    user_id = userinfo['sub']
    user = User.query.get(user_id)
    # insert user into table if not exist
    if not user:
        user = User(
            id=user_id,
            email=userinfo['email'],
            first_name=userinfo['given_name'],
            last_name=userinfo['family_name'],
        )
        user.insert()
    login_user(user)
    return redirect(url_for('index'))


@bp.route('/login')
def login():
    """Redirects to Auth0's login page."""
    # redirect user back to index page if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)
    return auth0.authorize_redirect(
        # generate the callback url
        redirect_uri=request.url_root
        + url_for('auth.callback')[1:]
    )


@bp.route('/logout')
@login_required
def logout():
    """Logs user out both from the issue tracker and auth0."""
    logout_user()

    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)
    params = {
        'returnTo': url_for('auth.login', _external=True),
        'client_id': '3silBpYY8BSfVWca3Q0suIwB8h24vMzz',
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
