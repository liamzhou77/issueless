"""Defines all SqlAlchemy models."""

from hashlib import md5

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

# Initialize extensions
db = SQLAlchemy()


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
    project = db.relationship(
        'Project',
        backref=db.backref(
            'user_projects', lazy='dynamic', cascade='all, delete-orphan'
        ),
    )

    def __init__(self, user, project, role=None):
        self.user = user
        self.project = project
        self.role = role

    def __repr__(self):
        return f'< User {self.user_id}, Project {self.project_id}, Role {self.role} >'

    def can(self, permission):
        return self.role and self.role.has_permission(permission)


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'< Project {self.id}, {self.title} >'

    def delete(self):
        """Deletes the input project."""
        db.session.delete(self)
        db.session.commit()


class Permission(object):
    """An object representation for permissions.

    Each permission's value is a distinct number which is power of two.  Having it this
    way makes all possible combinations of permissions have different values.
    """

    UPDATE_PROJECT = 1
    DELETE_PROJECT = 2
    INVITE_MEMBER = 4


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
                Permission.UPDATE_PROJECT,
                Permission.DELETE_PROJECT,
                Permission.INVITE_MEMBER,
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
