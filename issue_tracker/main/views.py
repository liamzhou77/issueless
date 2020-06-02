"""All views for main blueprint.

  Typical usage example:

  from main import views
"""

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.decorators import permission_required
from issue_tracker.main import bp
from issue_tracker.main.forms import InvitationForm
from issue_tracker.models import db, Notification, Permission, Project, User
from issue_tracker.validators import project_validation
from werkzeug.urls import url_parse


@bp.route('/')
def index():
    "Redirects to dashboard view."
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
            'invitor_name': f'{current_user.first_name} {current_user.last_name}',
            'project_title': project.title,
            'role_name': role_name,
        }
        invited_user.add_notification('invitation', data, target_id=project.id)
        db.session.commit()

        return redirect(url_for('main.project', id=project.id))

    return render_template(
        'project.html',
        title=project.title,
        project=project,
        role=user_project.role.name,
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
            'You can not add any more projects, you can only create 4 or less projects.'
            'Please delete one existing project before you add any more.'
        )
        return redirect(url_for('index'))

    title = request.form.get('title')
    description = request.form.get('description')

    error = project_validation(title, description)
    if error:
        flash(error)
        return redirect(url_for('index'))

    project = Project(title=title, description=description)
    current_user.add_project(project, 'Admin')
    db.session.commit()

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
    """

    title = request.form.get('title')
    description = request.form.get('description')

    error = project_validation(title, description)
    if error:
        flash(error)
        return redirect(url_for('index'))

    project = user_project.project
    project.title = title
    project.description = description
    db.session.commit()

    return redirect(url_for('index'))


@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
@permission_required(Permission.DELETE_PROJECT)
def delete_project(user_project):
    """Deletes a project.

    Args:
        user_project: A UserProject object returned from permission_required decorator,
        whose user_id belongs to the current user and project_id is the same as the one
        in the url.

    Returns:
        Redirect to dashboard view.
    """

    db.session.delete(user_project.project)
    db.session.commit()
    return redirect(url_for('index'))


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

    Returns:
        Redirect to the 'next' url.
    """

    project = Project.query.get(id)
    if not project:
        abort(404)

    notification = current_user.notifications.filter_by(
        name='invitation', target_id=id
    ).first()
    if not notification:
        abort(403)

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')

    if project.user_projects.count() >= 30:
        flash('Failed to join the project. The project does not have remaining spots.')
        return redirect(next_page)

    role_name = notification.get_data()['role_name']
    current_user.add_project(project, role_name)

    db.session.delete(notification)
    db.session.commit()

    return redirect(next_page)


@bp.route('/notifications')
@login_required
def notifications():
    """Returns notifications in json."""
    notifications = current_user.notifications.order_by(Notification.timestamp.desc())
    return jsonify(
        [
            {
                'notification_id': n.id,
                'name': n.name,
                'target_id': n.target_id,
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

    notification = get_notification(id)
    db.session.delete(notification)
    db.session.commit()

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)


def get_notification(id):
    """Gets a notification.

    Args:
        id: A notification's id to be queried.

    Aborts:
        403 Forbidden: A status code aborted if the notification does not belong to
            current user.
        404 Not Found: A status code aborted if notification does not exist.

    Returns:
        A notification whose id is the same as the input id.
    """

    notification = Notification.query.get(id)
    if not notification:
        abort(404)
    if notification.user_id != current_user.id:
        abort(403)
    return notification
