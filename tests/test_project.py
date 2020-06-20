import json

from issueless.models import db, Notification, Project, User, UserProject


def test_project(client, auth):
    auth.login(1)

    assert client.get('/projects/1').status_code == 200


def test_manage(client, auth):
    auth.login(1)

    assert client.get('/projects/1/manage').status_code == 200


def test_invalid_create(client, auth):
    auth.login(1)

    resp = client.post(
        '/projects/create', data={'title': '', 'description': ''}, follow_redirects=True
    )
    assert b'Please provide your project&#39;s title.' in resp.data

    resp = client.post(
        '/projects/create',
        data={'title': 'test_title', 'description': ''},
        follow_redirects=True,
    )
    assert b'Please provide your project&#39;s description.' in resp.data

    resp = client.post(
        '/projects/create',
        data={
            'title': 'This is a title with more than 50 characters...........',
            'description': 'awds',
        },
        follow_redirects=True,
    )
    assert b'Project&#39;s title can not be more than 50 character.' in resp.data

    resp = client.post(
        '/projects/create',
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
    assert (
        b'Project&#39;s description can not be more than 200 characters.' in resp.data
    )


def test_valid_create(client, auth):
    auth.login(1)
    resp = client.post(
        '/projects/create',
        data={'title': 'test_title_4', 'description': 'test_description_4'},
    )

    user_projects = User.query.get(1).user_projects
    assert user_projects.count() == 4

    new_user_project = UserProject.query.filter_by(user_id=1, project_id=4).first()
    role = new_user_project.role
    assert role.name == 'Admin'

    new_project = new_user_project.project
    assert new_project.title == 'test_title_4'
    assert new_project.description == 'test_description_4'
    assert 'http://localhost/dashboard' == resp.headers['Location']

    # test add fifth project
    resp = client.post(
        '/projects/create',
        data={'title': 'test_title_5', 'description': 'test_description_5'},
        follow_redirects=True,
    )
    user_projects = User.query.get(1).user_projects
    assert user_projects.count() == 4
    assert (
        b'You can only create or join 4 or less projects. Please delete or quit one '
        b'existing project before you add any more.' in resp.data
    )


def test_invalid_update(client, auth):
    auth.login(1)

    assert client.post('/projects/1/update', json={}).status_code == 400

    resp = client.post('/projects/1/update', json={'title': '', 'description': ''})
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == "Please provide your project's title."

    resp = client.post(
        '/projects/1/update', json={'title': 'test_title', 'description': ''}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == "Please provide your project's description."

    resp = client.post(
        '/projects/1/update',
        json={
            'title': 'This is a title with more than 50 characters...........',
            'description': 'awds',
        },
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == "Project's title can not be more than 50 character."

    resp = client.post(
        '/projects/1/update',
        json={
            'title': 'awdsad.',
            'description': (
                'This is a description with more than 200 characters...................'
                '......................................................................'
                '......................................................................'
            ),
        },
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == "Project's description can not be more than 200 characters."

    resp = client.post(
        '/projects/1/update',
        json={'title': 'test_title_1', 'description': 'test_description_1'},
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'No changes have been made.'


def test_update_with_valid_data(client, auth):
    auth.login(1)

    resp = client.post(
        '/projects/1/update',
        json={'title': 'modified_title', 'description': 'modified_description'},
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']

    project = Project.query.get(1)
    assert 'modified_title' == project.title
    assert 'modified_description' == project.description


def test_delete(client, auth):
    auth.login(1)

    resp = client.post('/projects/1/delete')
    assert resp.status_code == 302
    assert 'http://localhost/dashboard' == resp.headers['Location']
    assert Project.query.get(1) is None

    assert (
        Notification.query.filter_by(name='project deleted', user_id=1).first() is None
    )
    assert (
        Notification.query.filter_by(name='project deleted', user_id=2).first()
        is not None
    )


def test_invite_get(client, auth):
    auth.login(1)

    resp = client.get('/projects/1/invite')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']
    assert not data['users']

    resp = client.get('/projects/1/invite?search=test')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['users'] == [
        {
            'fullname': 'David Johnson',
            'username': 'test_username_1',
            'avatar': 'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc'
            '?d=identicon&s=60',
            'joined': True,
        },
        {
            'fullname': 'Ryan Cooper',
            'username': 'test_username_3',
            'avatar': 'https://www.gravatar.com/avatar/19f84906f4412abf6066aaa92fe9d6c1'
            '?d=identicon&s=60',
            'joined': False,
        },
        {
            'fullname': 'Wade Tom',
            'username': 'test_username_2',
            'avatar': 'https://www.gravatar.com/avatar/3c4f419e8cd958690d0d14b3b89380d3'
            '?d=identicon&s=60',
            'joined': True,
        },
    ]

    resp = client.get('/projects/1/invite?search=test_username_1%20')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['users'] == [
        {
            'fullname': 'David Johnson',
            'username': 'test_username_1',
            'avatar': 'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc'
            '?d=identicon&s=60',
            'joined': True,
        }
    ]

    resp = client.get('/projects/1/invite?search=Wade%20To')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['users'] == [
        {
            'fullname': 'Wade Tom',
            'username': 'test_username_2',
            'avatar': 'https://www.gravatar.com/avatar/3c4f419e8cd958690d0d14b3b89380d3'
            '?d=identicon&s=60',
            'joined': True,
        }
    ]

    resp = client.get('/projects/1/invite?search=test1@gmail.c')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert not data['users']

    resp = client.get('/projects/1/invite?search=test1@gmail.com')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['users'] == [
        {
            'fullname': 'David Johnson',
            'username': 'test_username_1',
            'avatar': 'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc'
            '?d=identicon&s=60',
            'joined': True,
        }
    ]


def test_invalid_invitation_post(client, auth):
    auth.login(1)

    assert client.post('/projects/1/invite', json={}).status_code == 400

    resp = client.post(
        '/projects/1/invite', json={'username': 'unknown', 'role': 'Developer'}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'Please provide a valid username.'

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_3', 'role': 'Unknown'}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'Please provide a valid role.'

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_3', 'role': 'Admin'}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'Please provide a valid role.'

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_1', 'role': 'Reviewer'}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'You can not invite yourself to your project.'

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_2', 'role': 'Reviewer'}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'User is already a member of the project.'

    project = Project.query.get(1)
    for num in range(4, 32):
        user = User(
            sub=f'test_sub_{num}',
            username=f'testusername{num}',
            email=f'test{num}@gmail.com',
            first_name='testfirstname',
            last_name='testlastname',
        )
        db.session.add(user)
        user.add_project(project, 'Developer')
    db.session.commit()
    assert project.user_projects.count() == 30

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_3', 'role': 'Developer'}
    )
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'You can only have 30 or less members in one project.'


def test_valid_invite_post(client, auth):
    auth.login(1)

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_3', 'role': 'Developer'}
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']

    notification = Notification.query.get(3)
    assert notification.name == 'invitation'
    assert notification.target_id == 1
    assert notification.user_id == 3
    data = notification.get_data()
    assert data['invitorName'] == 'David Johnson'
    assert data['projectTitle'] == 'test_title_1'
    assert data['roleName'] == 'Developer'
    timestamp = notification.timestamp

    resp = client.post(
        '/projects/1/invite', json={'username': 'test_username_3', 'role': 'Developer'}
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']
    notification = Notification.query.get(4)
    assert notification.timestamp > timestamp
    assert Notification.query.get(3) is None


def test_invalid_join(client, auth):
    auth.login(3)

    assert client.post('/projects/4/join').status_code == 404
    assert client.post('/projects/1/join').status_code == 403


def test_valid_join(client, auth):
    auth.login(3)

    resp = client.post('/projects/2/join')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']

    user_project = UserProject.query.filter_by(user_id=3, project_id=2).first()
    assert user_project is not None
    assert user_project.role.name == 'Developer'

    assert Notification.query.get(1) is None

    notification = Notification.query.filter_by(
        name='join project', user_id=user_project.project.get_admin().id
    ).first()
    assert notification is not None


def test_quit(client, auth):
    auth.login(2)

    resp = client.post('/projects/1/quit')
    assert resp.status_code == 302
    assert 'http://localhost/dashboard' == resp.headers['Location']

    assert UserProject.query.filter_by(user_id=2, project_id=1).first() is None
    assert (
        Notification.query.filter_by(name='quit project', user_id=1).first() is not None
    )


def test_invalid_delete_member(client, auth):
    auth.login(1)

    assert client.post('/projects/1/delete-member', json={}).status_code == 400

    resp = client.post('/projects/1/delete-member', json={'user_id': 3})
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'The user to be deleted is not a member of the project.'

    resp = client.post('/projects/1/delete-member', json={'user_id': 1})
    assert resp.status_code == 422
    data = json.loads(resp.data)
    assert not data['success']
    assert data['error'] == 'You can not remove yourself from the project.'


def test_valid_delete_member(client, auth):
    auth.login(1)
    resp = client.post('/projects/1/delete-member', json={'user_id': 2})
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']
    assert UserProject.query.filter_by(user_id=2, project_id=1).first() is None
    assert (
        Notification.query.filter_by(name='user removed', user_id=2).first() is not None
    )


def test_members(client, auth):
    auth.login(1)

    resp = client.get('/projects/1/members')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']
    assert data['members'] == [
        {
            'avatar': 'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc'
            '?d=identicon&s=60',
            'name': 'David Johnson',
            'username': 'test_username_1',
            'email': 'test1@gmail.com',
            'role': 'Admin',
            'timestamp': 'Fri, 05 Jun 2020 04:00:27 GMT',
        },
        {
            'avatar': 'https://www.gravatar.com/avatar/3c4f419e8cd958690d0d14b3b89380d3'
            '?d=identicon&s=60',
            'name': 'Wade Tom',
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'role': 'Reviewer',
            'timestamp': 'Fri, 05 Jun 2020 04:00:27 GMT',
        },
    ]

    resp = client.get('/projects/1/members?search=wade%20')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']
    assert data['members'] == [
        {
            'avatar': 'https://www.gravatar.com/avatar/3c4f419e8cd958690d0d14b3b89380d3'
            '?d=identicon&s=60',
            'name': 'Wade Tom',
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'role': 'Reviewer',
            'timestamp': 'Fri, 05 Jun 2020 04:00:27 GMT',
        }
    ]

    resp = client.get('/projects/1/members?search=test1@')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['success']
    assert data['members'] == [
        {
            'avatar': 'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc'
            '?d=identicon&s=60',
            'name': 'David Johnson',
            'username': 'test_username_1',
            'email': 'test1@gmail.com',
            'role': 'Admin',
            'timestamp': 'Fri, 05 Jun 2020 04:00:27 GMT',
        }
    ]
