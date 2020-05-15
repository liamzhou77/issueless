def test_index(client):
    rsp = client.get('/')
    assert 'http://localhost/dashboard' == rsp.headers['Location']


def test_projects_section(client, auth):
    auth.login()
    rsp = client.get('/dashboard')
    assert rsp.status_code == 200
    assert b'test_title_1' in rsp.data and b'test_title_2' in rsp.data
