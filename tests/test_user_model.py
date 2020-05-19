from issue_tracker.models import Project, User


def test_avatar(app):
    user = User.query.filter_by(email='test_email_1').first()
    assert user.avatar(128) == (
        'https://www.gravatar.com/avatar/e9e45d50e714809e07c9a06113d9a3a5?d='
        'identicon&s=128'
    )


def test_insert_project(app):
    user = User.query.first()
    user.insert_project(
        Project(title='test_title_4', description='test_description_4'), 'Admin'
    )

    new_project = Project.query.get(4)
    assert new_project.title == 'test_title_4'
    assert new_project.description == 'test_description_4'

    user_project = user.user_projects.filter_by(project_id=4).first()
    role = user_project.role
    assert role.name == 'Admin'
