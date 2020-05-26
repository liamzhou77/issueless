from flask_login import LoginManager

from issue_tracker.models import User

login = LoginManager()
login.login_view = 'auth.login'


@login.user_loader
def load_user(user_id):
    """Reloads the user object from the user ID stored in the session."""
    return User.query.get(user_id)
