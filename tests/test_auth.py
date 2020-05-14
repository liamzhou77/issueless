def test_callback(client):
    assert client.get('/auth/callback').status_code == 401


def test_logout(client):
    rsp = client.get('/auth/logout')
    assert 'http://localhost/auth/login' == rsp.headers['Location']
