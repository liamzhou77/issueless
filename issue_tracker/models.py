from hashlib import md5

from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'

# association table for users and projects
user_project = db.Table(
    'user_project',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
)


class User(UserMixin, db.Model):
    """Represents users table.

    Uses UserMixin to implement flask-login's required items.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    projects = db.relationship(
        'Project',
        secondary=user_project,
        lazy='dynamic',
        backref=db.backref("users", lazy='dynamic'),
    )

    def __repr__(self):
        return f"<User '{self.id}' '{self.first_name} {self.last_name}' '{self.email}>'"

    def insert(self):
        """Inserts user into users table."""
        db.session.add(self)
        db.session.commit()

    def avatar(self, size):
        digest = md5(self.email.lower().encode()).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


class Project(db.Model):
    """Represents projects table."""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<Project '{self.id} {self.title}>'"

    def insert(self):
        """Inserts project into projects table."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Deletes project from projects table."""
        db.session.delete(self)
        db.session.commit()

    def update(self):
        """Updates project info."""
        db.session.commit()


@login.user_loader
def load_user(user_id):
    """Reloads the user object from the user ID stored in the session."""
    return User.query.get(user_id)
