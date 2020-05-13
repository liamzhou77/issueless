import os

from flaskr import create_app
from flaskr.models import db
import pytest

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite://'})
    app_context = app.app_context()

    app_context.push()

    db.create_all()
    db.session.execute(_data_sql)
    db.session.commit()

    yield app

    db.session.remove()
    db.drop_all()

    app_context.pop()


@pytest.fixture
def client(app):
    return app.test_client()
