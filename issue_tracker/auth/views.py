from flask import abort, current_app, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user
from six.moves.urllib.parse import urlencode
from werkzeug.urls import url_parse

from issue_tracker.auth import bp
from issue_tracker.models import User
from issue_tracker.oauth import configure_oauth


@bp.route('/callback')
def callback():
    """Logs users in after they are authenticated by Auth0."""
    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)

    # Hard coding callback route in browser would result in various exceptions. In this
    # case an Unauthorized error with 404 status code would be more appropriate,
    # because only Auth0 is authorized to access this callback route, this route should
    # not be accessible by users.
    try:
        auth0.authorize_access_token()
    except Exception:
        abort(404)

    rsp = auth0.get('userinfo')
    userinfo = rsp.json()

    sub = userinfo['sub']
    user = User.query.filter_by(sub=sub).first()
    # insert user into table if not exist
    if not user:
        user = User(
            sub, userinfo['email'], userinfo['given_name'], userinfo['family_name'],
        )
        user.insert()
    login_user(user, remember=True)

    next_page = session.get('next_page')
    session.pop('next_page')

    return redirect(next_page)


@bp.route('/login')
def login():
    """Redirects to Auth0's login page."""
    # redirect user back to index page if they are already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)

    # Store 'next' url parameter in session if it exists, so the callback view can
    # redirect users back to where they were.
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    session['next_page'] = next_page

    return auth0.authorize_redirect(
        redirect_uri=request.url_root
        + url_for('auth.callback')[1:]  # generate the callback url
    )


@bp.route('/logout')
def logout():
    """Logs user out both from the issue tracker and auth0."""
    # Redirect users to login page if they are not authenticated. Use this instead of
    # @login_required, so users would not be redirected back to logout view after
    # authentification.
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    logout_user()

    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)
    params = {
        'returnTo': url_for('auth.login', _external=True),
        'client_id': '3silBpYY8BSfVWca3Q0suIwB8h24vMzz',
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@bp.route('/test/login', methods=['POST'])
def _login():
    """This view is only for testing."""
    if current_app.config['TESTING']:
        user_id = request.form['id']
        user = User.query.get(user_id)

        login_user(user)
        return f'User {user_id} logged in'
    else:
        abort(404)
