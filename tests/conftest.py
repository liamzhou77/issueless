import os

import pytest

from issue_tracker import create_app
from issue_tracker.models import db, Role

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """Creates an application context and a mock database for each test."""
    app = create_app(
        {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': (
                'postgresql://liamzhou@localhost/test_issue_tracker'
            ),
            'WTF_CSRF_ENABLED': False,
        }
    )
    app_context = app.app_context()

    app_context.push()

    db.create_all()
    Role.insert_roles()  # this method is tested in test_role_model.py
    db.session.execute(_data_sql)
    db.session.commit()

    yield app

    db.session.remove()
    db.drop_all()

    app_context.pop()


@pytest.fixture
def client(app):
    """Returns a test client."""
    return app.test_client()


class AuthActions(object):
    """Actions to authorize test client."""

    def __init__(self, client):
        self._client = client

    def login(self):
        return self._client.post('/auth/test/login', data={'id': 1})


@pytest.fixture
def auth(client):
    """Return the AuthActions object."""
    return AuthActions(client)
