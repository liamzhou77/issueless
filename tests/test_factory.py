from issue_tracker import create_app


def test_config(app):
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
