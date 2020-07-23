import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask, redirect, request
from flask_migrate import Migrate
from pyngrok import ngrok

from issueless import auth
from issueless import errors
from issueless import issue
from issueless import main
from issueless import project
from issueless.login import login
from issueless.models import db
from issueless.oauth import oauth


def create_app(test_config=None):
    """Creates a flask instance and declares extensions and blueprints."""
    app = Flask(__name__, instance_relative_config=True)

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
    app.register_blueprint(issue.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(project.bp)
    app.add_url_rule('/dashboard', endpoint='index')

    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/issueless.log', maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s '
                    '[in %(pathname)s:%(lineno)d]'
                )
            )
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

    @app.before_request
    def before_request():
        if request.url.startswith('http://') and app.env != "development":
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, 301)

    @app.shell_context_processor
    def make_shell_context():
        """Defines shell context for debugging."""
        from issueless.models import (
            Comment,
            File,
            Issue,
            Notification,
            Project,
            Role,
            User,
            UserProject,
        )

        return {
            'db': db,
            'User': User,
            'Project': Project,
            'UserProject': UserProject,
            'Role': Role,
            'Notification': Notification,
            'Issue': Issue,
            'File': File,
            'Comment': Comment,
        }

    @app.cli.command("insert-roles")
    def insert_roles():
        from issueless.models import Role

        Role.insert_roles()

    def start_ngrok():
        url = ngrok.connect(5000)
        print(' * Tunnel URL:', url)

    if app.config['START_NGROK']:
        start_ngrok()

    return app
