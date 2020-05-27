from issue_tracker.models import db


def test_index(client, auth):
    auth.login()
    rsp = client.get('/')
    assert rsp.status_code == 200
    assert (
        b'test_title_1---Admin' in rsp.data
        and b'test_title_2---Reviewer' in rsp.data
        and b'test_title_3---Developer' in rsp.data
    )

    db.session.execute('DELETE FROM user_project where user_id = 1 and project_id = 1;')
    rsp = client.get('/')
    assert b'delete' not in rsp.data

    db.session.execute('INSERT INTO user_project values (1, 1, 1);')
    rsp = client.get('/')
    assert b'delete' in rsp.data
