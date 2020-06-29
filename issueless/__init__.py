from datetime import timedelta
import os

from flask import Flask
from flask_migrate import Migrate

from issueless import auth
from issueless import errors
from issueless import main
from issueless import project
from issueless.login import login
from issueless.models import db
from issueless.oauth import oauth


def create_app(test_config=None):
    """Creates a flask instance and declares extensions and blueprints."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=(
            'sqlite:///' + os.path.join(app.instance_path, 'issueless.db')
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REMEMBER_COOKIE_DURATION=timedelta(days=3, hours=1),
    )
    app.config.from_pyfile('config.py', silent=True)
    if test_config is not None:
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
    app.register_blueprint(errors.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(project.bp)
    app.add_url_rule('/dashboard', endpoint='index')

    @app.shell_context_processor
    def make_shell_context():
        """Defines shell context for debugging."""
        from issueless.models import Notification, Project, Role, User, UserProject

        return {
            'db': db,
            'User': User,
            'Project': Project,
            'UserProject': UserProject,
            'Role': Role,
            'Notification': Notification,
        }

    return app
