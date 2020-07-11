from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issueless.decorators import permission_required
from issueless.models import db, Issue, Permission, Project, User, UserProject
from issueless.project import bp
from issueless.project.helpers import (
    change_role_validation,
    create_validation,
    edit_validation,
    invite_validation,
    join_validation,
    remove_member_validation,
)


@bp.route('/<int:id>')
@login_required
@permission_required(Permission.READ_PROJECT)
def project(user_project):
    project = user_project.project
    return render_template(
        'project.html',
        title=project.title,
        current_user_project=user_project,
        member_user_projects=project.user_projects.order_by(UserProject.timestamp),
        open_issues=project.issues.filter_by(status='Open').order_by(Issue.timestamp),
        in_progress_issues=project.issues.filter_by(
            status='In Progress', priority='High'
        )
        .order_by(Issue.timestamp)
        .union_all(
            project.issues.filter_by(status='In Progress', priority='Medium').order_by(
                Issue.timestamp
            )
        )
        .union_all(
            project.issues.filter_by(status='In Progress', priority='Low').order_by(
                Issue.timestamp
            )
        ),
        resolved_issues=project.issues.filter_by(status='Resolved').order_by(
            Issue.timestamp
        ),
        closed_issues=project.issues.filter_by(status='Closed').order_by(
            Issue.timestamp
        ),
    )


@bp.route('/create', methods=['POST'])
@login_required
def create():
    """Creates a new project.

    Args:
        title：
            in: formData
            type: string
            description: The new project's title.
        description：
            in: formData
            type: string
            description: The new project's description.

    Responses:
        302:
            description: Redirect to dashboard page.
    """

    title = request.form.get('title')
    description = request.form.get('description')

    error = create_validation(title, description)
    if error is not None:
        flash(error)
    else:
        project = Project(title=title, description=description)
        current_user.add_project(project, 'Admin')
        db.session.commit()

    return redirect(url_for('index'))


@bp.route('/<int:id>/edit', methods=['POST'])
@login_required
@permission_required(Permission.MANAGE_PROJECT)
def edit(user_project):
    """Edits a project's information.

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
            and project_id is the same as the query parameter - id.
        title:
            in: formData
            type: string
            description: The project's new title.
        description:
            in: formData
            type: string
            description: The project's new description.

    Responses:
        200:
            description: Update successfully.
        400:
            description: Bad request.
        403:
            description: Current user is not a member of the project or does not have
                the permission.
        404:
            description: Project does not exist.
        422:
            description: Unprocessable.
    """

    body = request.get_json()
    title = body.get('title')
    description = body.get('description')
    if None in (title, description):
        abort(400)

    project = user_project.project
    edit_validation(project, title, description)

    project.title = title
    project.description = description
    db.session.commit()

    return {'success': True}


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.MANAGE_PROJECT)
def delete(user_project):
    """Deletes a project.

    Deletes a project. Notifies all other members.

    Produces:
        application/json
        text/html

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
                and project_id is the same as the query parameter - id.

    Responses:
        302:
            description: Redirect to dashboard page.
        403:
            description: Current user is not a member of the project or does not have
                the permission.
        404:
            description: Project does not exist.
    """

    project = user_project.project
    for user in project.users:
        if user != current_user:
            user.add_basic_notification('project deleted', project.title)

    db.session.delete(project)
    db.session.commit()

    return redirect(url_for('index'))


@bp.route('/<int:id>/invite', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MANAGE_PROJECT)
def invite(user_project):
    """Searches for users to be invited or sends invitation.

    GET:
        Args:
            search:
                in: query
                type: string
                description: The search term.

        Responses:
            200:
                description: Searched user's information.

    POST:
        Args:
            target:
                in: json
                type: string
                description: The target to be searched with.
            role:
                in: json
                type: string
                description: Role name to be assigned to the invited user.

        Responses:
            200:
                description: Invitation successfully sent.
            400:
                description: Bad request.
            422:
                description: Unprocessable.

    Produces:
        application/json
        text/html

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
                and project_id is the same as the query parameter - id.

    Responses:
        403:
            description: Current user is not a member of the project or does not have
                the permission.
        404:
            description: Project does not exist.
    """

    project = user_project.project

    if request.method == 'POST':
        body = request.get_json()
        target = body.get('target')
        role_name = body.get('role')
        if None in (target, role_name):
            abort(400)

        user = invite_validation(project, target, role_name)
        if user is not None:
            data = {
                'avatar': current_user.avatar(),
                'fullname': current_user.fullname(),
                'projectTitle': project.title,
                'roleName': role_name,
            }
            user.add_notification('invitation', data, target_id=project.id)
            db.session.commit()

        return {'success': True}

    search_term = request.args.get('search')
    if search_term is None:
        return {'success': True, 'users': []}
    if search_term[-1] == ' ':
        search_term = search_term[:-1]
    ilike_regex = f'{search_term}%'

    users = (
        User.query.filter(
            User.username.ilike(ilike_regex)
            | db.func.concat(User.first_name, ' ', User.last_name).ilike(ilike_regex)
        )
        .order_by(db.func.concat(User.first_name, ' ', User.last_name))
        .limit(10)
        .all()
    )

    return {
        'success': True,
        'users': [
            {
                'fullname': user.fullname(),
                'username': user.username,
                'avatar': user.avatar(),
                'joined': user in project.users,
            }
            for user in users
        ],
    }


@bp.route('/<int:id>/join', methods=['POST'])
@login_required
def join(id):
    """Joins the project.

    Joins the project. Notifies admin.

    Produces:
        application/json
        text/html

    Args:
        id:
            in: path
            type: int
            string: The project's id.

    Responses:
        200:
            description: Succesfully joined the project.
        403:
            description: Current user does not have the invitation.
        422:
            description: Unprocessable.
    """

    notification = current_user.notifications.filter_by(
        name='invitation', target_id=id
    ).first()
    if notification is None:
        abort(403)

    project = Project.query.get(id)
    join_validation(project)

    role_name = notification.get_data()['roleName']
    current_user.add_project(project, role_name)

    admin = project.get_admin()
    admin.add_basic_notification('join project', project.title)

    db.session.delete(notification)
    db.session.commit()

    return {'success': True}


@bp.route('/<int:id>/quit', methods=['POST'])
@login_required
@permission_required(Permission.QUIT_PROJECT)
def quit(user_project):
    """Quits from the project.

    Quits from the project. Notifies admin.

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
                and project_id is the same as the query parameter - id.

    Responses:
        302:
            description: Redirect to dashboard page.
        403:
            description: Current user is not a member of the project or does not have
                the permission.
        404:
            description: Project does not exist.
    """

    project = user_project.project
    db.session.delete(user_project)
    project.get_admin().add_basic_notification('quit project', project.title)
    db.session.commit()

    return redirect(url_for('index'))


@bp.route('/<int:id>/remove-member', methods=['POST'])
@login_required
@permission_required(Permission.MANAGE_PROJECT)
def remove_member(user_project):
    """Removes a user from the project.

    Removes a user from the project. Notifies the user.

    Produces:
        application/json
        text/html

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
                and project_id is the same as the query parameter - id.
        user_id:
            in: json
            type: int
            description: Id of the user to be deleted.

    Responses:
        200:
            description: Remove successfully.
        400:
            description: Bad request.
        403:
            description: Current user is not a member of the project or does not have
                the permission.
        404:
            description: Project does not exist.
        422:
            description: Target user is not a member of the project or is the current
                user who is admin.
    """

    body = request.get_json()
    user_id = body.get('user_id')
    if user_id is None:
        abort(400)

    project = user_project.project
    user = User.query.get_or_404(user_id)
    user_project = remove_member_validation(project, user)

    db.session.delete(user_project)
    user.add_basic_notification('user removed', project.title)
    db.session.commit()

    return {'success': True}


@bp.route('/<int:id>/change-role', methods=['POST'])
@login_required
@permission_required(Permission.MANAGE_PROJECT)
def change_role(user_project):
    """Changes a member's role.

    Changes a member's role. If member's previous role is Reviewer, demote to Developer.
    Otherwise, promote to Reviewer.

    Produces:
        application/json

    Args:
        user_project:
            in: permission_required() decorator
            type: UserProject
            description: A UserProject object whose user_id belongs to the current user
                and project_id is the same as the query parameter - id.
        user_id:
            in: json
            type: int
            description: Id of the user to be promoted or demoted.

    Responses:
        200:
            description: Change successfully.
        400:
            description: Bad request.
        404:
            description: User not found.
        422:
            description: Unprocessable.
    """

    body = request.get_json()
    user_id = body.get('user_id')
    if user_id is None:
        abort(400)

    project = user_project.project
    user = User.query.get_or_404(user_id)
    user_project = change_role_validation(project, user)

    user_project.change_role()
    db.session.commit()

    return {'success': True}
