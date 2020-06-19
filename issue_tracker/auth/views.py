from flask import abort, current_app, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user
from six.moves.urllib.parse import urlencode

from issue_tracker.auth import bp
from issue_tracker.models import db, User
from issue_tracker.oauth import configure_oauth


@bp.route('/callback')
def callback():
    """Executes authorization after user is authticated by Auth0.

    Responses:
        302:
            description: Redirect to the location specified in session key 'next'.
        401:
            description: New user did not agree to give access to their email and
                profile.
        403:
            description: Forbidden.
    """

    if request.args.get('error') is not None:
        abort(401)

    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)
    # Hard coding callback route in browser would result in various exceptions. Only
    # Auth0 is authorized to access this callback route.
    try:
        auth0.authorize_access_token()
    except Exception:
        abort(403)

    resp = auth0.get('userinfo')
    userinfo = resp.json()
    sub = userinfo['sub']
    user = User.query.filter_by(sub=sub).first()
    if user is None:
        user = User(
            sub=sub,
            email=userinfo['email'],
            username=userinfo['https://issue-tracker-7:auth0:com/username'],
            first_name=userinfo['given_name'],
            last_name=userinfo['family_name'],
        )
        db.session.add(user)
        db.session.commit()
    login_user(user, remember=True)

    next_page = session.pop('next', None)
    if next_page is None:
        next_page = url_for('index')
    print(next_page)
    return redirect(next_page)


@bp.route('/login')
def login():
    """Initializes Auth0 authentification.

    Responses:
        302:
            description: Redirect to Auth0's login page.
    """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    client_secret = current_app.config['AUTH0_CLIENT_SECRET']
    auth0 = configure_oauth(client_secret)
    return auth0.authorize_redirect(
        redirect_uri=request.url_root
        + url_for('auth.callback')[1:]  # generate the callback url
    )


@bp.route('/logout')
def logout():
    """Logs user out from the web app and Auth0.

    Logs user out from flask_login and Auth0. Auth0 would redirect user back to the
    login view after log out.

    Responses:
        302:
            description: Redirect to Auth0's logout page.
    """

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
    """Logs test user in."""
    if current_app.config['TESTING']:
        user_id = request.form['id']
        user = User.query.get(user_id)

        login_user(user)
        return f'User {user_id} logged in'
    else:
        abort(404)


@bp.route('/test/logout', methods=['POST'])
def _logout():
    """Logs test user out."""
    if current_app.config['TESTING']:
        logout_user()
        return 'User logged out'
    else:
        abort(404)
