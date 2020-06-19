def test_directly_call_callback(client):
    resp = client.get('/auth/callback')
    assert resp.status_code == 403


def test_logout_if_not_login(client):
    resp = client.get('/auth/logout')
    assert 'http://localhost/auth/login' == resp.headers['Location']


def test_logout_if_login(client, auth):
    auth.login(1)
    resp = client.get('/auth/logout')
    assert resp.headers['Location'].startswith(
        'https://issue-tracker-7.auth0.com/v2/logout?returnTo='
    )
