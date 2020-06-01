from issue_tracker.models import db, Project, User


def test_avatar(app):
    user = User.query.filter_by(email='test1@gmail.com').first()
    assert user.avatar(128) == (
        'https://www.gravatar.com/avatar/245cf079454dc9a3374a7c076de247cc?d='
        'identicon&s=128'
    )


def test_insert_project(app):
    user = User.query.first()
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
    user = User.query.get(3)
    user.add_notification('invitation', 3, target_id=1)
    notification = user.notifications.first()
    assert notification.name == 'invitation'
    assert notification.get_data() == 3
    assert notification.target_id == 1
    assert notification.user_id == 3

    timestamp = notification.timestamp

    user.add_notification('invitation', 3, target_id=1)
    assert user.notifications.count() == 1
    assert user.notifications.first().timestamp > timestamp
