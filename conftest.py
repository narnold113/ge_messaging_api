import pytest
from messaging_api import create_app, db as _db
import os
import json

@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app()
    os.environ['FLASK_TESTING'] = "1"

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app

@pytest.fixture(scope='session')
def test_app(app):
    return app.test_client()

@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""

    _db.app = app

    return _db

@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session

class UserActions(object):
    def __init__(self, test_app):
        self._client = test_app

    def create_user(self):
        json_body = {
            "first_name": "Test",
            "last_name": "User",
            "primary_email": "john.doe@gmail.com"
        }
        return self._client.post('/user', data=json.dumps(json_body))

@pytest.fixture
def user(test_app):
    return UserActions(test_app)

class MessageActions(object):
    def __init__(self, test_app):
        self._client = test_app

    def create_message(self, sender_user_id, recipient_user_id):
        json_body = {
            "sender_user_id": sender_user_id,
            "recipient_user_id": recipient_user_id,
            "message_body": "Test Message Body"
        }
        return self._client.post('/message', data=json.dumps(json_body))

@pytest.fixture
def message(test_app):
    return MessageActions(test_app)