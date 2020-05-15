def test_index(client):
    rsp = client.get('/')
    assert 'http://localhost/dashboard/' == rsp.headers['Location']
