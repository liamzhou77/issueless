import json

from issue_tracker.models import Notification


def test_index(client, auth):
    auth.login(1)
    assert 'http://localhost/dashboard' == client.get('/').headers['Location']


def test_dashboard(client, auth):
    auth.login(1)
    resp = client.get('/dashboard')
    assert resp.status_code == 200


def test_notifications(client, auth):
    auth.login(2)
    resp = client.get('/notifications')
    assert resp.status_code == 200

    data = json.loads(resp.data)
    assert data['success']
    notifications = data['notifications']
    assert len(notifications) == 1
    notification = notifications[0]
    assert notification['notificationId'] == 2
    assert notification['name'] == 'invitation'
    assert notification['targetId'] == 3
    assert notification['data'] == {
        "invitorName": "Ryan Cooper",
        "projectTitle": "test_title_3",
        "roleName": "Developer",
    }


def test_delete_notification(client, auth):
    auth.login(3)

    assert client.post('/notifications/2/delete').status_code == 403
    assert client.post('/notifications/10/delete').status_code == 404

    resp = client.post('/notifications/1/delete')
    assert resp.status_code == 200
    assert not Notification.query.get(1)
    data = json.loads(resp.data)
    assert data['success']
