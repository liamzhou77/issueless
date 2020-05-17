from issue_tracker.models import User


def test_index(client):
    rsp = client.get('/')
    assert 'http://localhost/dashboard' == rsp.headers['Location']


def test_dashboard_projects_section(client, auth):
    auth.login()
    rsp = client.get('/dashboard')
    assert rsp.status_code == 200
    assert (
        b'test_title_1---Admin' in rsp.data
        and b'test_title_2---Admin' in rsp.data
        and b'test_title_3---Admin' in rsp.data
    )


def test_post_project_with_invalid_data(client, auth):
    auth.login()

    rsp = client.post(
        '/projects', data={'title': '', 'description': ''}, follow_redirects=True
    )
    assert b'title is required.' in rsp.data

    rsp = client.post(
        '/projects',
        data={'title': 'test_title', 'description': ''},
        follow_redirects=True,
    )
    assert b'description is required.' in rsp.data

    rsp = client.post(
        '/projects',
        data={
            'title': 'This is a title with more than 50 characters...........',
            'description': 'awds',
        },
        follow_redirects=True,
    )
    assert b'title can not be more than 50 character.' in rsp.data

    rsp = client.post(
        '/projects',
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


def test_post_project_with_valid_data(client, auth):
    auth.login()
    rsp = client.post(
        '/projects', data={'title': 'test_title_4', 'description': 'test_description_4'}
    )

    user_projects = User.query.get(1).user_projects
    assert user_projects.count() == 4
    new_project = user_projects.filter_by(user_id=1, project_id=4).first().project
    assert new_project.title == 'test_title_4'
    assert new_project.description == 'test_description_4'
    assert 'http://localhost/dashboard' == rsp.headers['Location']
    # test add fifth project
    rsp = client.post(
        '/projects',
        data={'title': 'test_title_5', 'description': 'test_description_5'},
        follow_redirects=True,
    )
    assert user_projects.count() == 4
    assert (
        b'You can not add any more projects, you can only create 4 or less projects.'
        in rsp.data
    )
