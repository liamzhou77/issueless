import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate

from flaskr import auth
from flaskr import dashboard
from flaskr import errors
from flaskr.models import db, login
from flaskr.oauth import oauth


def create_app(test_config=None):
    """Creates a flask instance and declares extensions and blueprints."""
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=(
            'sqlite:///' + os.path.join(app.instance_path, 'flaskr.db')
        ),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize extension objects with app
    Bootstrap(app)
    db.init_app(app)
    login.init_app(app)
    Migrate(app, db)
    oauth.init_app(app)

    # register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='index')
    app.register_blueprint(errors.bp)

    # shell context for debugging
    @app.shell_context_processor
    def make_shell_context():
        from flaskr.models import User

        return {'db': db, 'User': User}

    return app
