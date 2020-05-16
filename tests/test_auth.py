from flask import session


def test_directly_call_callback(client):
    rsp = client.get('/auth/callback')
    assert rsp.status_code == 404
    assert b'Not Found' in rsp.data


def test_login_redirect(client, auth):
    with client:
        client.get('/auth/login')
        assert session['next_page'] == '/dashboard'
        client.get('/auth/login?next=')
        assert session['next_page'] == '/dashboard'

    auth.login()
    rsp = client.get('/auth/login')
    assert 'http://localhost/dashboard' == rsp.headers['Location']


def test_logout_if_not_login(client):
    rsp = client.get('/auth/logout')
    assert 'http://localhost/auth/login' == rsp.headers['Location']


def test_logout_if_login(client, auth):
    auth.login()
    rsp = client.get('/auth/logout')
    assert rsp.headers['Location'].startswith(
        'https://issue-tracker-7.auth0.com/v2/logout?returnTo='
    )
