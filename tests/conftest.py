import os

import pytest

from issue_tracker import create_app
from issue_tracker.models import db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    app = create_app(
        {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'WTF_CSRF_ENABLED': False,
        }
    )
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


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self):
        return self._client.post('/auth/test/login', data={'id': 1})


@pytest.fixture
def auth(client):
    return AuthActions(client)
