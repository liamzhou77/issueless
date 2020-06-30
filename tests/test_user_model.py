from issueless.models import db, Notification, Project, User


def test_avatar(app):
    user = User.query.filter_by(email='test1@gmail.com').first()
    assert user.avatar() == (
        'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc?d='
        'identicon&s=68'
    )


def test_add_project(app):
    user = User.query.get(1)
    user.add_project(
        Project(title='test_title_4', description='test_description_4'), 'Admin'
    )
    db.session.commit()

    new_project = Project.query.get(4)
    assert new_project.title == 'test_title_4'
    assert new_project.description == 'test_description_4'

    user_project = user.user_projects.filter_by(project_id=4).first()
    role = user_project.role
    assert role.name == 'Admin'


def test_add_notification(app):
    user = User.query.get(2)

    old_timestamp = Notification.query.get(2).timestamp
    user.add_notification('invitation', {}, 3)
    assert Notification.query.get(2) is None
    notification = Notification.query.get(3)
    assert notification is not None
    assert notification.timestamp > old_timestamp

    for i in range(2, 51):
        user.add_notification('test', {})
    assert user.notifications.count() == 50
    user.add_notification('test', {})
    assert user.notifications.count() == 50
    assert Notification.query.get(2) is None
