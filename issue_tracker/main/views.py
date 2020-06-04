"""All views for main blueprint.

  Typical usage example:

  from main import views
"""

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.decorators import permission_required
from issue_tracker.main import bp
from issue_tracker.main.forms import InvitationForm
from issue_tracker.models import (
    db,
    Notification,
    Permission,
    Project,
    User,
    UserProject,
)
from issue_tracker.validators import project_validation
from werkzeug.urls import url_parse


@bp.route('/')
def index():
    """Redirects to dashboard view."""
    return redirect(url_for('main.dashboard'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard template."""
    user_projects = current_user.user_projects
    return render_template(
        'dashboard.html', title='Dashboard', user_projects=user_projects
    )


@bp.route('/projects/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.READ_PROJECT)
def project(user_project):
    """Renders the project template.

    Renders the project template and implements the invitation form validation.

    Args:
        user_project: A UserProject object returned from permission_required decorator,
            whose user_id belongs to the current user and project_id is the same as the
            one in the url.

    Aborts:
        403 Forbidden: A status code aborted if current user is not a member of
            the project or does not have the permission.
        404 Not Found: A status code aborted if project does not exist.
    """

    project = user_project.project
    invitation_form = InvitationForm(user_projects=project.user_projects)

    if invitation_form.validate_on_submit():
        if project.user_projects.count() >= 30:
            flash('You can only have 30 or less members in one project.')
            return redirect(url_for('main.project', id=project.id))

        invited_email = request.form.get('email')
        role_name = request.form.get('role')

        invited_user = User.query.filter_by(email=invited_email).first()

        data = {
            'invitorName': f'{current_user.first_name} {current_user.last_name}',
            'projectTitle': project.title,
            'roleName': role_name,
        }
        invited_user.add_notification('invitation', data, target_id=project.id)
        db.session.commit()

        return redirect(url_for('main.project', id=project.id))

    return render_template(
        'project.html',
        user_project=user_project,
        user_projects=project.user_projects.order_by(UserProject.role_id).all(),
        invitation_form=invitation_form,
    )


@bp.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    """Creates a new project.

    Form Data:
        title: A project's title.
        description: A project's description.

    Returns:
        Redirect to dashboard view.
    """

    # Each user can create 4 projects at most.
    if current_user.user_projects.count() >= 4:
        flash(
            'You can not create any more projects, you can only create or join 4 or '
            'less projects. Please delete or quit one existing project before you add '
            'any more.'
        )
        return redirect(url_for('index'))

    title = request.form.get('title')
    description = request.form.get('description')

    error = project_validation(title, description)
    if not error:
        project = Project(title=title, description=description)
        current_user.add_project(project, 'Admin')
        db.session.commit()
    else:
        flash(error)

    return redirect(url_for('index'))


@bp.route('/projects/<int:id>/update', methods=['POST'])
@login_required
@permission_required(Permission.UPDATE_PROJECT)
def update_project(user_project):
    """Updates a project's information.

    Args:
        user_project: A UserProject object returned from permission_required decorator,
        whose user_id belongs to the current user and project_id is the same as the one
        in the url.

    Returns:
        Redirect to dashboard view.

    Aborts:
        403 Forbidden: A status code aborted if current user is not a member of
            the project or does not have the permission.
        404 Not Found: A status code aborted if project does not exist.
    """

    title = request.form.get('title')
    description = request.form.get('description')

    error = project_validation(title, description)
    if not error:
        project = user_project.project
        project.title = title
        project.description = description
        db.session.commit()
    else:
        flash(error)

    return redirect(url_for('index'))


@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.DELETE_PROJECT)
def delete_project(user_project):
    """Deletes a project.

    Deletes a project. Add notification to all other members.

    Args:
        user_project: A UserProject object returned from permission_required decorator,
        whose user_id belongs to the current user and project_id is the same as the one
        in the url.

    Aborts:
        403 Forbidden: A status code aborted if current user is not a member of
            the project or does not have the permission.
        404 Not Found: A status code aborted if project does not exist.

    Returns:
        Redirect to dashboard view.
    """

    project = user_project.project

    users = project.users
    for user in users:
        if user != current_user:
            user.add_notification('project deleted', {'projectTitle': project.title})

    db.session.delete(project)
    db.session.commit()

    return redirect(url_for('index'))


@bp.route('/projects/<int:id>/delete-member', methods=['POST'])
@login_required
def delete_member(id):
    """Deletes user from the project.

    Deletes user from the project. If current user is admin of the project, delete the
    user who has the same id as the one in the form['user_id']. Otherwise, remove
    current user from the project.

    Args:
        id: An url parameter indicating the project's id.

    Form Data:
        user_id: Id of the user to be removed.

    Aborts:
        400 Bad Request: A status code aborted if current user is admin and the forn
        403 Forbidden: A status code aborted if current user is not a member of
            the project or the user to be removed is not a member of the project.
        404 Not Found: A status code aborted if project does not exist or the user to
            be removed does not exist.

    Returns:
        Redirect to index view.
    """

    project = Project.query.get_or_404(id)
    user_project = current_user.user_projects.filter_by(project=project).first()
    next_page = None

    if not user_project:
        abort(403)

    if user_project.role.name == 'Admin':
        user_id = request.form.get('user_id')
        if not user_id:
            abort(400)

        user = User.query.get_or_404(user_id)
        user_project = project.user_projects.filter_by(user=user).first()

        if not user_project or user == current_user:
            abort(403)

        user.add_notification(
            'user removed', {'projectTitle': project.title},
        )

        next_page = url_for('main.project', id=id)
    else:
        admin = project.get_admin()
        admin.add_notification(
            'quit project',
            {
                'userName': f'{current_user.first_name} {current_user.last_name}',
                'projectTitle': project.title,
            },
        )

        next_page = url_for('index')

    db.session.delete(user_project)
    db.session.commit()

    return redirect(next_page)


@bp.route('/projects/<int:id>/add-member', methods=['POST'])
@login_required
def add_member(id):
    """Adds a new member to the project.

    Args:
        id: An url parameter indicating the project's id. The project id would never be
            the same as a project that current user has already joined, because to join
            the project user must have an invtiation to the project. Invitation would
            never be sent if the user is already a member of the project.
        next: A url parameter indicating what url to be redirected to.

    Aborts:
        403 Forbidden: A status code aborted if current user does not have the
            invitation.
        404 Not Found: A status code aborted if project does not exist.

    Returns:
        Redirect to the 'next' url.
    """

    project = Project.query.get_or_404(id)

    notification = current_user.notifications.filter_by(
        name='invitation', target_id=id
    ).first()
    if not notification:
        abort(403)

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')

    error = None
    if current_user.user_projects.count() >= 4:
        error = (
            'You can not join any more projects, you can only create or join 4 or less '
            'projects. Please delete or quit one existing project before you add any '
            'more.'
        )
    elif project.user_projects.count() >= 30:
        error = 'Failed to join the project. The project does not have remaining spots.'

    if not error:
        role_name = notification.get_data()['roleName']
        current_user.add_project(project, role_name)

        admin = project.get_admin()
        admin.add_notification(
            'join project',
            {
                'userName': f'{current_user.first_name} {current_user.last_name}',
                'projectTitle': project.title,
            },
        )

        db.session.delete(notification)

        db.session.commit()
    else:
        flash(error)

    return redirect(next_page)


@bp.route('/notifications')
@login_required
def notifications():
    """Returns notifications in json."""
    notifications = current_user.notifications.order_by(
        Notification.timestamp.desc()
    ).all()
    return jsonify(
        [
            {
                'notificationId': n.id,
                'name': n.name,
                'targetId': n.target_id,
                'data': n.get_data(),
                'timestamp': n.timestamp,
            }
            for n in notifications
        ]
    )


@bp.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
def delete_notification(id):
    """Deletes a notification.

    Args:
        id: A notification's id.
        next: A url parameter indicating what url to be redirected to.

    Aborts:
        403 Forbidden: A status code aborted if the notification does not belong to
            current user.
        404 Not Found: A status code aborted if notification does not exist.

    Returns:
        Redirect to the 'next' url.
    """

    notification = Notification.query.get_or_404(id)

    if notification.user != current_user:
        abort(403)

    db.session.delete(notification)
    db.session.commit()

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)
