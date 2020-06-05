from issue_tracker.models import Notification, UserProject


def test_index(client, auth):
    auth.login(1)
    assert 'http://localhost/dashboard' == client.get('/').headers['Location']


def test_dashboard(client, auth):
    auth.login(1)
    rsp = client.get('/dashboard')
    assert rsp.status_code == 200


def test_delete_notification(client, auth):
    auth.login(3)

    assert client.post('/notifications/2/delete').status_code == 403
    assert client.post('/notifications/10/delete').status_code == 404

    rsp = client.post('/notifications/1/delete')
    assert rsp.status_code == 302
    assert not Notification.query.get(1)
    assert 'http://localhost/dashboard' == rsp.headers['Location']

    auth.logout()
    auth.login(2)

    rsp = client.post('/notifications/2/delete?next=/projects/2')
    assert rsp.status_code == 302
    assert not Notification.query.get(2)
    assert 'http://localhost/projects/2' == rsp.headers['Location']
