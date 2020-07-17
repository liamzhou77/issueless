from hashlib import md5
import json
from time import time

from flask_login import current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (db.Index('full_name', 'first_name', 'last_name'),)

    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    projects = association_proxy('user_projects', 'project')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    created_issues = db.relationship(
        'Issue',
        backref='creator',
        lazy='dynamic',
        primaryjoin='User.id == Issue.creator_id',
    )
    assigned_issues = db.relationship(
        'Issue',
        backref='assignee',
        lazy='dynamic',
        primaryjoin='User.id == Issue.assignee_id',
    )
    files = db.relationship('File', backref='uploader', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'< User {self.email}, {self.fullname()}, {self.username} >'

    def add_project(self, project, role_name):
        """Adds the input project with input role under current user.

        Args:
            project: A project to be added.
            role_name: A role's name the user should have in project.
        """

        role = Role.query.filter_by(name=role_name).first()
        user_project = UserProject(user=self, project=project, role=role)
        db.session.add(user_project)

    def avatar(self):
        """Generates the avatar link for user.

        Returns:
            A string of the avatar url.
        """

        digest = md5(self.email.lower().encode()).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s=68'

    def add_notification(self, name, data, target_id=None):
        """Adds a new notification.

        Adds a new notification. Deletes the oldest notification if adding the new one
        would make user's notification count exceed 50.

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

        if self.notifications.count() >= 50:
            db.session.delete(
                self.notifications.order_by(Notification.timestamp).first()
            )

        new_notification = Notification(
            name=name, payload_json=json.dumps(data), target_id=target_id, user=self
        )
        db.session.add(new_notification)

    def add_basic_notification(self, name, title):
        self.add_notification(
            name,
            {
                'avatar': current_user.avatar(),
                'fullname': current_user.fullname(),
                'projectTitle': title,
            },
        )

    def fullname(self):
        return f'{self.first_name} {self.last_name}'

    @staticmethod
    def _insert_test_users():
        project = Project.query.filter_by(title='Issueless').first()
        for i in range(30):
            user = User(
                sub=f'auth0|{i}',
                email=f'test{i}@gmail.com',
                first_name=f'firstname{i}',
                last_name=f'lastname{i}',
                username=f'username{i}',
            )

            if i < 10:
                user.add_project(project, 'Reviewer')
            elif i < 20:
                user.add_project(project, 'Developer')

            db.session.add(user)
        db.session.commit()


class UserProject(db.Model):
    __tablename__ = 'user_projects'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    timestamp = db.Column(db.Float, index=True, default=time, nullable=False)

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
        return (
            f'< User {self.user.fullname()}, Project {self.project.title}, Role '
            f'{self.role.name} >'
        )

    def can(self, permission):
        return self.role and self.role.has_permission(permission)

    def change_role(self):
        reviewer = Role.query.filter_by(name='Reviewer').first()
        developer = Role.query.filter_by(name='Developer').first()
        if self.role == reviewer:
            self.role = developer
        elif self.role == developer:
            self.role = reviewer


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    users = association_proxy('user_projects', 'user')
    issues = db.relationship(
        'Issue', backref='project', lazy='dynamic', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'< Project {self.title}, {self.description} >'

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
    MANAGE_ISSUES = 8


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
                Permission.MANAGE_ISSUES,
            ],
            'Reviewer': [
                Permission.READ_PROJECT,
                Permission.QUIT_PROJECT,
                Permission.MANAGE_ISSUES,
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
    __table_args__ = (db.Index('timestamp', 'is_read'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), index=True, nullable=False)
    target_id = db.Column(
        db.Integer
    )  # Representing what instance is the notification about
    timestamp = db.Column(db.Float, index=True, default=time, nullable=False)
    payload_json = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return (
            f'< Notification {self.user.fullname()}, {self.name}, {self.target_id}, '
            f'{self.payload_json}, {self.is_read}>'
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
            "isRead": self.is_read,
        }


class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(6), index=True)
    status = db.Column(db.String(11), default='Open', index=True, nullable=False)
    timestamp = db.Column(db.Float, index=True, default=time, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    files = db.relationship(
        'File', backref='issue', lazy='dynamic', cascade='all, delete-orphan'
    )
    comments = db.relationship(
        'Comment', backref='issue', lazy='dynamic', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'< Issue {self.title}, {self.status}, {self.priority}, creator '
            f'{self.creator.fullname()}, project {self.project.title} >'
        )


class File(db.Model):
    __tablename__ = 'files'
    __table_args__ = (
        db.UniqueConstraint('issue_id', 'filename', name='issue_filename'),
    )

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(), nullable=False)
    size = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.Float, index=True, default=time, nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)

    def __repr__(self):
        return (
            f'< File {self.filename}, Uploader {self.uploader.fullname()}, Issue '
            f'{self.issue.title} >'
        )


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000), nullable=False)
    timestamp = db.Column(db.Float, index=True, default=time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)

    def __repr__(self):
        return f'< Comment {self.id}, {self.user.fullname()}, {self.issue.title} >'
