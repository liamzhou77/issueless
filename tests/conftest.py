import shutil
import os

import pytest

from issueless import create_app
from issueless.models import db, Role

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """Creates an application context and a mock database for each test."""
    app = create_app(
        {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': (
                'postgresql://liamzhou@localhost/test_issueless'
            ),
            'WTF_CSRF_ENABLED': False,
            'UPLOAD_PATH': 'tests/uploads',
        }
    )
    app_context = app.app_context()

    app_context.push()

    db.create_all()
    Role.insert_roles()  # this method is tested in test_role_model.py
    db.session.execute(_data_sql)
    db.session.commit()
    for i in range(1, 5):
        os.makedirs(os.path.join(app.config['UPLOAD_PATH'], str(i)))

    yield app

    db.session.remove()
    db.drop_all()
    for i in range(1, 5):
        shutil.rmtree(
            os.path.join(app.config['UPLOAD_PATH']), ignore_errors=True,
        )

    app_context.pop()


@pytest.fixture
def client(app):
    """Returns a test client."""
    return app.test_client()


class AuthActions(object):
    """Actions to authorize test client."""

    def __init__(self, client):
        self._client = client

    def login(self, id):
        return self._client.post('/auth/test/login', data={'id': id})

    def logout(self):
        return self._client.post('/auth/test/logout')


@pytest.fixture
def auth(client):
    """Return the AuthActions object."""
    return AuthActions(client)
