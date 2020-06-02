def test_permission_required(client, auth):
    auth.login(2)

    assert client.post('/projects/2/delete').status_code == 302
    assert client.post('/projects/1/delete').status_code == 403
    assert client.post('/projects/3/delete').status_code == 403
    assert client.post('/projects/4/delete').status_code == 404
