from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'


class User(UserMixin, db.Model):
    """Represents users table.

    Uses UserMixin to implement flask-login's required items.
    """

    __tablename__ = 'users'

    id = db.Column(db.String(), primary_key=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<User '{self.first_name} {self.last_name}' '{self.email}'"

    def insert(self):
        """Inserts user into users table."""
        db.session.add(self)
        db.session.commit()


@login.user_loader
def load_user(user_id):
    """Reloads the user object from the user ID stored in the session."""
    return User.query.get(user_id)
