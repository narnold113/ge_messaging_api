import pytest
import json

def test_create_user(test_app, user, session):
    response = user.create_user()
    assert response.status_code == 200
    assert session.query(User).count() == 1

# def test_login(test_app, auth, session):
#     assert test_app.post('/api/v1/login', headers={"Content-Type": "application/json"}, data=json.dumps({})).status_code == 200
#     auth.signup()
#     response = auth.login()
#     assert b'access_token' in response.data
#     assert b'refresh_token' in response.data