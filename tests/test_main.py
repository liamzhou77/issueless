from issue_tracker.models import db, Notification, Project, User, UserProject


def test_dashboard(client, auth):
    auth.login(1)
    rsp = client.get('/dashboard')
    assert rsp.status_code == 200
    assert (
        b'test_title_1---Admin' in rsp.data
        and b'test_title_2---Reviewer' in rsp.data
        and b'test_title_3---Developer' in rsp.data
    )

    db.session.execute('DELETE FROM user_project where user_id = 1 and project_id = 1;')
    rsp = client.get('/dashboard')
    assert b'delete' not in rsp.data

    db.session.execute('INSERT INTO user_project values (1, 1, 1);')
    rsp = client.get('/dashboard')
    assert b'delete' in rsp.data


def test_create_project_with_invalid_data(client, auth):
    auth.login(1)

    rsp = client.post(
        '/projects/create', data={'title': '', 'description': ''}, follow_redirects=True
    )
    assert b'title is required.' in rsp.data

    rsp = client.post(
        '/projects/create',
        data={'title': 'test_title', 'description': ''},
        follow_redirects=True,
    )
    assert b'description is required.' in rsp.data

    rsp = client.post(
        '/projects/create',
        data={
            'title': 'This is a title with more than 50 characters...........',
            'description': 'awds',
        },
        follow_redirects=True,
    )
    assert b'title can not be more than 50 character.' in rsp.data

    rsp = client.post(
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
    assert b'description can not be more than 200 characters.' in rsp.data


def test_create_project_with_valid_data(client, auth):
    auth.login(1)
    rsp = client.post(
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
    assert 'http://localhost/dashboard' == rsp.headers['Location']

    # test add fifth project
    rsp = client.post(
        '/projects/create',
        data={'title': 'test_title_5', 'description': 'test_description_5'},
        follow_redirects=True,
    )
    user_projects = User.query.get(1).user_projects
    assert user_projects.count() == 4
    assert (
        b'You can not create any more projects, you can only create or join 4 or less projects.'
        in rsp.data
    )


def test_delete_project(client, auth):
    auth.login(1)

    rsp = client.post('/projects/1/delete')
    assert 'http://localhost/dashboard' == rsp.headers['Location']
    assert not Project.query.get(1)


def test_update_project_with_invalid_data(client, auth):
    auth.login(1)

    rsp = client.post(
        '/projects/1/update',
        data={'title': '', 'description': ''},
        follow_redirects=True,
    )
    assert b'title is required.' in rsp.data

    rsp = client.post(
        '/projects/1/update',
        data={'title': 'test_title', 'description': ''},
        follow_redirects=True,
    )
    assert b'description is required.' in rsp.data

    rsp = client.post(
        '/projects/1/update',
        data={
            'title': 'This is a title with more than 50 characters...........',
            'description': 'awds',
        },
        follow_redirects=True,
    )
    assert b'title can not be more than 50 character.' in rsp.data

    rsp = client.post(
        '/projects/1/update',
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
    assert b'description can not be more than 200 characters.' in rsp.data


def test_update_project_with_valid_data(client, auth):
    auth.login(1)

    rsp = client.post(
        '/projects/1/update',
        data={'title': 'modified_title', 'description': 'modified_description'},
    )
    assert 'http://localhost/dashboard' == rsp.headers['Location']

    project = Project.query.get(1)
    assert 'modified_title' == project.title
    assert 'modified_description' == project.description


def test_invitation_with_invalid_data(client, auth):
    auth.login(1)

    rsp = client.post('/projects/1', data={'email': '', 'role': ''})
    assert (
        b'Please enter an email address.' in rsp.data
        and b'Not a valid choice' in rsp.data
    )

    rsp = client.post('/projects/1', data={'email': 'test3', 'role': 'Developer'})
    assert b'Please enter a valid email address.' in rsp.data

    rsp = client.post(
        '/projects/1', data={'email': 'test4@gmail.com', 'role': 'Developer'}
    )
    assert b'Unknown email address. Please try again.' in rsp.data

    rsp = client.post(
        '/projects/1', data={'email': 'test1@gmail.com', 'role': 'Developer'}
    )
    assert b'You can not invite yourself to your project.' in rsp.data

    rsp = client.post(
        '/projects/1', data={'email': 'test2@gmail.com', 'role': 'Developer'}
    )
    assert b'User is already a member of the project.' in rsp.data


def test_invitation_with_valid_data(client, auth):
    auth.login(1)

    rsp = client.post(
        '/projects/1', data={'email': 'test3@gmail.com', 'role': 'Developer'}
    )
    assert 'http://localhost/projects/1' == rsp.headers['Location']

    notification = Notification.query.get(3)
    assert notification.name == 'invitation'
    assert notification.target_id == 1
    assert notification.user_id == 3
    data = notification.get_data()
    assert data['invitorName'] == 'test_first_name_1 test_last_name_1'
    assert data['projectTitle'] == 'test_title_1'
    assert data['roleName'] == 'Developer'

    timestamp = notification.timestamp
    client.post('/projects/1', data={'email': 'test3@gmail.com', 'role': 'Developer'})
    notification = Notification.query.get(4)
    assert notification.timestamp > timestamp

    project = Project.query.get(1)
    for num in range(4, 32):
        user = User(
            sub=f'test_sub_{num}',
            email=f'test{num}@gmail.com',
            first_name=f'test_first_name_{num}',
            last_name=f'test_last_name_{num}',
        )
        db.session.add(user)
        user.add_project(project, 'Developer')
    db.session.commit()

    assert project.user_projects.count() == 30

    rsp = client.post(
        '/projects/1',
        data={'email': 'test3@gmail.com', 'role': 'Developer'},
        follow_redirects=True,
    )
    assert b'You can only have 30 or less members in one project.' in rsp.data
    assert project.user_projects.count() == 30


def test_delete_notification(client, auth):
    auth.login(3)

    assert client.post('/notifications/2/delete').status_code == 403
    assert client.post('/notifications/10/delete').status_code == 404

    rsp = client.post('/notifications/1/delete')
    assert rsp.status_code == 302
    assert 'http://localhost/dashboard' == rsp.headers['Location']

    auth.logout()
    auth.login(2)

    rsp = client.post('/notifications/2/delete?next=/projects/2')
    assert rsp.status_code == 302
    assert 'http://localhost/projects/2' == rsp.headers['Location']


def test_add_member(client, auth):
    auth.login(3)

    assert client.post('/projects/4/add-member').status_code == 404
    assert client.post('/projects/1/add-member').status_code == 403

    rsp = client.post('/projects/2/add-member?next=/dashboard')
    assert rsp.status_code == 302
    assert 'http://localhost/dashboard' == rsp.headers['Location']

    user_project = UserProject.query.filter_by(user_id=3, project_id=2).first()
    assert user_project
    assert user_project.role.name == 'Developer'

    assert not Notification.query.get(1)
