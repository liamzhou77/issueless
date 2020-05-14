from flask import session, url_for


def test_callback(client):
    rsp = client.get('/auth/callback')
    assert rsp.status_code == 404
    assert b'Not Found' in rsp.data


def test_login(client, auth):
    with client:
        client.get('/auth/login')
        assert session['next_page'] == url_for('index')
        client.get('/auth/login?next=')
        assert session['next_page'] == url_for('index')

    auth.login()
    rsp = client.get('/auth/login')
    assert 'http://localhost/' == rsp.headers['Location']


def test_logout(client, auth):
    rsp = client.get('/auth/logout')
    assert 'http://localhost/auth/login' == rsp.headers['Location']

    auth.login()
    rsp = client.get('/auth/logout')
    assert rsp.headers['Location'].startswith(
        'https://issue-tracker-7.auth0.com/v2/logout?returnTo='
    )
