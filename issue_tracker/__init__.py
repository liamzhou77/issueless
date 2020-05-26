from datetime import timedelta
import os

from flask import Flask, redirect, url_for
from flask_migrate import Migrate

from issue_tracker import auth
from issue_tracker import dashboard
from issue_tracker import errors
from issue_tracker.login import login
from issue_tracker.models import db
from issue_tracker.oauth import oauth


def create_app(test_config=None):
    """Creates a flask instance and declares extensions and blueprints."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=(
            'sqlite:///' + os.path.join(app.instance_path, 'issue_tracker.db')
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REMEMBER_COOKIE_DURATION=timedelta(days=3, hours=1),
    )

    app.config.from_pyfile('config.py', silent=True)
    if test_config:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login.init_app(app)
    Migrate(app, db)
    oauth.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/dashboard', endpoint='index')
    app.register_blueprint(errors.bp)

    @app.route('/')
    @app.route('/index')
    def index():
        """Redirects user to dashboard view."""
        return redirect(url_for('dashboard.dashboard'))

    @app.shell_context_processor
    def make_shell_context():
        """Defines shell context for debugging."""
        from issue_tracker.models import Project, Role, User, UserProject

        return {
            'db': db,
            'User': User,
            'Project': Project,
            'UserProject': UserProject,
            'Role': Role,
        }

    return app
