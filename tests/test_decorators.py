def test_permission_required(client, auth):
    auth.login(2)

    assert client.post('/projects/1/delete').status_code == 403
    assert client.post('/projects/3/delete').status_code == 403
    assert client.post('/projects/10/delete').status_code == 404


def test_access_issue_permission_required(client, auth):
    auth.login(3)

    assert client.get('/projects/10/issues/1').status_code == 404
    assert client.get('/projects/2/issues/1').status_code == 403
    assert client.get('/projects/1/issues/10').status_code == 404
    assert client.get('/projects/3/issues/1').status_code == 400
    assert client.get('/projects/1/issues/1').status_code == 400


def test_edit_issue_permission_required(client, auth):
    auth.login(3)

    assert client.post('/projects/10/issues/1/edit').status_code == 404
    assert client.post('/projects/2/issues/1/edit').status_code == 403
    assert client.post('/projects/1/issues/10/edit').status_code == 404
    assert client.post('/projects/3/issues/1/edit').status_code == 400
    assert client.post('/projects/1/issues/3/edit').status_code == 400
    assert client.post('/projects/1/issues/4/edit').status_code == 400
    assert client.post('/projects/1/issues/2/edit').status_code == 403


def test_delete_issue_permission_required(client, auth):
    auth.login(3)

    assert client.post('/projects/10/issues/1/delete').status_code == 404
    assert client.post('/projects/2/issues/1/delete').status_code == 403
    assert client.post('/projects/1/issues/10/delete').status_code == 404
    assert client.post('/projects/3/issues/1/delete').status_code == 400
    assert client.post('/projects/1/issues/2/delete').status_code == 403
    assert client.post('/projects/1/issues/1/delete').status_code == 302


def test_assign_issue_permission_required(client, auth):
    auth.login(3)

    assert client.post('/projects/10/issues/1/assign').status_code == 404
    assert client.post('/projects/2/issues/1/assign').status_code == 403
    assert client.post('/projects/1/issues/10/assign').status_code == 404
    assert client.post('/projects/3/issues/1/assign').status_code == 400
    assert client.post('/projects/1/issues/2/assign').status_code == 400
    assert client.post('/projects/1/issues/1/assign').status_code == 403


def test_close_issue_permission_required(client, auth):
    auth.login(3)

    assert client.post('/projects/10/issues/1/close').status_code == 404
    assert client.post('/projects/2/issues/1/close').status_code == 403
    assert client.post('/projects/1/issues/10/close').status_code == 404
    assert client.post('/projects/3/issues/1/close').status_code == 400
    assert client.post('/projects/1/issues/3/close').status_code == 400
    assert client.post('/projects/1/issues/4/close').status_code == 400
    assert client.post('/projects/1/issues/1/close').status_code == 403


def test_resolve_issue_permission_required(client, auth):
    auth.login(3)

    assert client.post('/projects/10/issues/1/resolve').status_code == 404
    assert client.post('/projects/2/issues/1/resolve').status_code == 403
    assert client.post('/projects/1/issues/10/resolve').status_code == 404
    assert client.post('/projects/3/issues/1/resolve').status_code == 400
    assert client.post('/projects/1/issues/1/resolve').status_code == 400
    assert client.post('/projects/1/issues/2/resolve').status_code == 403


def test_comment_and_upload_permission_required(client, auth):
    auth.login(3)

    assert client.post('/projects/10/issues/1/upload').status_code == 404
    assert client.post('/projects/2/issues/1/upload').status_code == 403
    assert client.post('/projects/1/issues/10/upload').status_code == 404
    assert client.post('/projects/3/issues/1/upload').status_code == 400
    assert client.post('/projects/1/issues/1/upload').status_code == 400

