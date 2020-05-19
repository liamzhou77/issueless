from hashlib import md5

from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

# Initialize extensions
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'


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

    projects = association_proxy('user_projects', 'project')

    def __repr__(self):
        return f'< User {self.id}, {self.first_name} {self.last_name}, {self.email} >'

    def insert(self):
        """Inserts user into users table."""
        db.session.add(self)
        db.session.commit()

    def insert_project(self, project, role):
        """Inserts the input project with input role under current user."""
        r = Role.query.filter_by(name=role).first()
        r.user_projects.append(UserProject(self, project))
        db.session.commit()

    def avatar(self, size):
        digest = md5(self.email.lower().encode()).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


class UserProject(db.Model):
    __tablename__ = 'user_project'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_projects', lazy='dynamic'))
    project = db.relationship('Project')

    def __init__(self, user, project, role=None):
        self.user = user
        self.project = project
        self.role = role

    def __repr__(self):
        return f'< User {self.user_id}, Project {self.project_id}, Role {self.role} >'


class Project(db.Model):
    """Represents projects table."""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'< Project {self.id}, {self.title} >'

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


class Permission(object):
    """An object representation for permissions.

    Each permission's value is a distinct number which is power of two.  Having it this
    way makes all possible combinations of permissions have different values.
    """

    update_project = 1
    delete_project = 2
    invite_member = 4


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(9), unique=True, nullable=False)
    permissions = db.Column(db.Integer, nullable=False)

    user_projects = db.relationship('UserProject', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'< Role {self.id}, {self.name}, {self.permissions} >'

    def has_permission(self, permission):
        """Checks if the self role has the input permission."""
        return (
            self.permissions & permission == permission
        )  # use bitwise and to check if permission exists

    def add_permission(self, permission):
        """Adds the input permission if it does not exist in the self role."""
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        """Removes the input permission if it exists in the self role."""
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permissions(self):
        """Sets the self role's permission value to 0."""
        self.permissions = 0

    @staticmethod
    def insert_roles():
        """Inserts roles into databse with their specific permissions."""
        role_permissions = {
            'Admin': [
                Permission.update_project,
                Permission.delete_project,
                Permission.invite_member,
            ],
            'Reviewer': [],
            'Developer': [],
        }
        # Update roles' permissions value instead of inserting new records if role
        # already exists.
        for r, permissions in role_permissions.items():
            role = Role.query.filter_by(name=r).first()
            if not role:
                role = Role(name=r, permissions=0)
            role.reset_permissions()
            for permission in permissions:
                role.add_permission(permission)
            db.session.add(
                role
            )  # will be ignored if the role is already in the database
        db.session.commit()


@login.user_loader
def load_user(user_id):
    """Reloads the user object from the user ID stored in the session."""
    return User.query.get(user_id)
