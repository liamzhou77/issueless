from datetime import datetime
from hashlib import md5
import json

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.Index('user_name', 'first_name', 'last_name'),)

    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    projects = association_proxy('user_projects', 'project')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def __repr__(self):
        return (
            f'< User {self.id}, {self.email}, {self.username}, {self.first_name} '
            f'{self.last_name} >'
        )

    def add_project(self, project, role_name):
        """Adds the input project with input role under current user.

        Args:
            project: A project to be added.
            role_name: A role's name the user should have in project.
        """

        role = Role.query.filter_by(name=role_name).first()
        user_project = UserProject(user=self, project=project, role=role)
        db.session.add(user_project)

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
            if notification is not None:
                db.session.delete(notification)

        new_notification = Notification(
            name=name, payload_json=json.dumps(data), target_id=target_id, user=self
        )
        db.session.add(new_notification)

    def fullname(self):
        return f'{self.first_name} {self.last_name}'


class UserProject(db.Model):
    __tablename__ = 'user_project'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id'), index=True, nullable=False
    )
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.utcnow, nullable=False
    )

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

    def to_dict(self):
        return {
            'avatar': self.user.avatar(60),
            'name': self.user.fullname(),
            'username': self.user.username,
            'email': self.user.email,
            'role': self.role.name,
            'timestamp': self.timestamp,
        }


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    users = association_proxy('user_projects', 'user')

    def __repr__(self):
        return f'< Project {self.id}, {self.title} >'

    def get_admin(self):
        """Gets the admin user in the project."""
        return (
            self.user_projects.filter_by(
                role=Role.query.filter_by(name='Admin').first()
            )
            .first()
            .user
        )


class Permission(object):
    """An object representation for permissions.

    Each permission's value is a distinct number which is power of two.  Having it this
    way makes all possible combinations of permissions have different values.
    """

    READ_PROJECT = 1
    MANAGE_PROJECT = 2
    QUIT_PROJECT = 4
    GET_MEMBERS = 8


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
                Permission.MANAGE_PROJECT,
                Permission.GET_MEMBERS,
            ],
            'Reviewer': [
                Permission.READ_PROJECT,
                Permission.QUIT_PROJECT,
                Permission.GET_MEMBERS,
            ],
            'Developer': [Permission.READ_PROJECT, Permission.QUIT_PROJECT],
        }

        # Update roles' permissions value instead of inserting new records if role
        # already exists.
        for r, permissions in role_permissions.items():
            role = Role.query.filter_by(name=r).first()
            if role is None:
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

    def __repr__(self):
        return (
            f'< Notification {self.id}, {self.name}, {self.target_id}, '
            f'{self.payload_json}, {self.timestamp} >'
        )

    def get_data(self):
        return json.loads(str(self.payload_json))

    def to_dict(self):
        return {
            'notificationId': self.id,
            'name': self.name,
            'targetId': self.target_id,
            'data': self.get_data(),
            'timestamp': self.timestamp,
        }
