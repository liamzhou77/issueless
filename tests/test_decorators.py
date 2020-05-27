def test_permission_required(client, auth):
    auth.login()

    rsp = client.post('/projects/1/delete')
    assert 'http://localhost/' == rsp.headers['Location']

    assert client.post('/projects/2/delete').status_code == 403

    assert client.post('/projects/4/delete').status_code == 404
