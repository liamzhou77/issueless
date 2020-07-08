from issueless.models import Issue

import json


def test_invalid_create(client, auth):
    auth.login(1)

    resp = client.post(
        '/projects/1/issues/create',
        data={'title': '', 'description': 'test_description'},
        follow_redirects=True,
    )
    assert b'Please provide the issue&#39;s title.' in resp.data

    resp = client.post(
        '/projects/1/issues/create',
        data={'title': 'test_title', 'description': ''},
        follow_redirects=True,
    )
    assert b'Please provide the issue&#39;s description.' in resp.data

    resp = client.post(
        '/projects/1/issues/create',
        data={
            'title': 'This is a title with more than 80 characters............................................',
            'description': 'awds',
        },
        follow_redirects=True,
    )
    assert b'Issue&#39;s title can not be more than 80 character.' in resp.data

    resp = client.post(
        '/projects/1/issues/create',
        data={
            'title': 'awdsad.',
            'description': (
                'This is a description with more than 200 characters...................'
                '......................................................................'
                '......................................................................'
            ),
        },
        follow_redirects=True,
    )
    assert b'Issue&#39;s description can not be more than 200 characters.' in resp.data


def test_valid_create(client, auth):
    auth.login(1)

    old_issue_count = Issue.query.count()
    resp = client.post(
        '/projects/1/issues/create',
        data={'title': 'test_title', 'description': 'test_description'},
    )
    assert 'http://localhost/projects/1' == resp.headers['Location']
    assert Issue.query.count() == old_issue_count + 1
    new_issue = Issue.query.get(old_issue_count + 1)
    assert new_issue.title == 'test_title'
    assert new_issue.description == 'test_description'
    assert new_issue.priority is None
    assert new_issue.status == 'Open'
    assert new_issue.creator_id == 1
    assert new_issue.assignee_id is None
    assert new_issue.project_id == 1


# def test_invalid_edit(client, auth):
#     auth.login(3)

#     resp = client.post(
#         '/projects/1/issues/2/edit',
#         json={'title': '', 'description': 'test_description'},
#     )
#     assert resp.status_code == 422
#     data = json.loads(resp.data)
#     assert not data['success']
#     assert data['error'] == "Please provide the issue's title."

#     resp = client.post(
#         '/projects/1/issues/2/edit', json={'title': 'test_title', 'description': ''},
#     )
#     assert resp.status_code == 422
#     data = json.loads(resp.data)
#     assert not data['success']
#     assert data['error'] == "Please provide the issue's description."

#     resp = client.post(
#         '/projects/1/issues/2/edit',
#         json={
#             'title': 'This is a title with more than 80 characters............................................',
#             'description': 'awds',
#         },
#     )
#     assert data['error'] == "Issue's title can not be more than 80 character."

#     resp = client.post(
#         '/projects/1/issues/2/edit',
#         json={
#             'title': 'awdsad.',
#             'description': (
#                 'This is a description with more than 200 characters...................'
#                 '......................................................................'
#                 '......................................................................'
#             ),
#         },
#     )
#     assert data['error'] == "Issue's description can not be more than 200 characters."


def test_delete(client, auth):
    auth.login(2)

    assert Issue.query.get(2) is not None
    resp = client.post('/projects/1/issues/2/delete')
    assert resp.status_code == 200
    assert json.loads(resp.data)['success']
    assert Issue.query.get(2) is None


def test_invalid_assign(client, auth):
    auth.login(2)

    client.post('/projects/1/issues/1/assign', json={}).status_code == 400

    resp = client.post(
        '/projects/1/issues/1/assign', json={'priority': 'invalid', 'assignee_id': 3}
    )
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'Please provide a valid priority level.'

    assert (
        client.post(
            '/projects/1/issues/1/assign', json={'priority': 'High', 'assignee_id': 10}
        ).status_code
        == 404
    )

    resp = client.post(
        '/projects/1/issues/2/assign', json={'priority': 'High', 'assignee_id': 3}
    )
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'The issue has already been assigned to Ryan Cooper.'


def test_valid_assign(client, auth):
    auth.login(2)

    issue = Issue.query.get(1)
    assert issue.status == 'Open'
    resp = client.post(
        '/projects/1/issues/1/assign', json={'priority': 'Medium', 'assignee_id': 3}
    )
    assert resp.status_code == 200
    assert json.loads(resp.data)['success']
    assert issue.status == 'In Progress'
    assert issue.assignee_id == 3
