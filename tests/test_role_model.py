from issue_tracker.models import Role


def test_insert_roles(app):
    assert Role.query.count() == 3
    role_names = [role.name for role in Role.query.all()]
    role_ids = [role.id for role in Role.query.all()]
    assert (
        'Admin' in role_names and 'Reviewer' in role_names and 'Developer' in role_names
    )
    assert 1 in role_ids and 2 in role_ids and 3 in role_ids

    # Test if role records are updated instead of deleting.
    Role.insert_roles()
    assert Role.query.count() == 3
    role_ids = [role.id for role in Role.query.all()]
    assert 1 in role_ids and 2 in role_ids and 3 in role_ids
