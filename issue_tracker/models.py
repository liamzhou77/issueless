"""Defines all SqlAlchemy models.

  Typical usage example:

  user = User.query.get(1)
"""

from datetime import datetime
from hashlib import md5
import json

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

    projects = association_proxy('user_projects', 'project')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'< User {self.id}, {self.first_name} {self.last_name}, {self.email} >'

    def add_project(self, project, role_name):
        """Adds the input project with input role under current user.

        Args:
            project: A project to be added.
            role_name: A role's name the user should have in project.
        """

        role = Role.query.filter_by(name=role_name).first()
        new_user_project = UserProject(user=self, project=project, role=role)
        db.session.add(new_user_project)

    def avatar(self, size):
        """Generates the avatar link for user.

        Args:
            size: A number indicating the size of the avatar.

        Returns:
            A string of the avatar url.
        """

        digest = md5(self.email.lower().encode()).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def add_notification(self, name, data, target_id=None):
        """Adds a new notification.

        Args:
            name: A notification's name to be added.
            data: A notification data to be added.
            target_id: An id representing what instance is Notification about.
        """

        if name == 'invitation':
            notification = self.notifications.filter(
                Notification.name == name, Notification.target_id == target_id
            ).first()
            # If user has already received the invitation, delete it before
            # replacing it with the new one.
            if notification:
                db.session.delete(notification)

            new_notification = Notification(
                name=name, payload_json=json.dumps(data), target_id=target_id, user=self
            )
            db.session.add(new_notification)


class UserProject(db.Model):
    __tablename__ = 'user_project'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    user = db.relationship(
        'User',
        backref=db.backref(
            'user_projects', lazy='dynamic', cascade='all, delete-orphan'
        ),
    )
    project = db.relationship(
        'Project',
        backref=db.backref(
            'user_projects', lazy='dynamic', cascade='all, delete-orphan'
        ),
    )

    def __repr__(self):
        return f'< User {self.user_id}, Project {self.project_id}, Role {self.role} >'

    def can(self, permission):
        return self.role and self.role.has_permission(permission)


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), index=True, nullable=False)
    description = db.Column(db.String(), nullable=False)

    users = association_proxy('user_projects', 'user')

    def __repr__(self):
        return f'< Project {self.id}, {self.title} >'


class Permission(object):
    """An object representation for permissions.

    Each permission's value is a distinct number which is power of two.  Having it this
    way makes all possible combinations of permissions have different values.
    """

    READ_PROJECT = 1
    UPDATE_PROJECT = 2
    DELETE_PROJECT = 4
    INVITE_MEMBER = 8


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(9), unique=True, nullable=False)
    permissions = db.Column(db.Integer, nullable=False)

    user_projects = db.relationship('UserProject', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'< Role {self.id}, {self.name}, {self.permissions} >'

    def has_permission(self, permission):
        return (
            self.permissions & permission == permission
        )  # use bitwise and to check if permission exists

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permissions(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        """Inserts roles into databse with their specific permissions."""
        role_permissions = {
            'Admin': [
                Permission.READ_PROJECT,
                Permission.UPDATE_PROJECT,
                Permission.DELETE_PROJECT,
                Permission.INVITE_MEMBER,
            ],
            'Reviewer': [Permission.READ_PROJECT],
            'Developer': [Permission.READ_PROJECT],
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


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), index=True, nullable=False)
    target_id = db.Column(
        db.Integer
    )  # Representing what instance is the notification about
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow, nullable=False
    )
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
