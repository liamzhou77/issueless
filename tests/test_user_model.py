from issue_tracker.models import User


def test_avatar(app):
    user = User.query.filter_by(email='test_email_1').first()
    assert user.avatar(128) == (
        'https://www.gravatar.com/avatar/e9e45d50e714809e07c9a06113d9a3a5?d='
        'identicon&s=128'
    )
