"""All views for main blueprint.

  Typical usage example:

  from main import views
"""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.decorators import permission_required
from issue_tracker.main import bp
from issue_tracker.models import db, Permission, Project, Role, User
from issue_tracker.main.forms import InvitationForm
from issue_tracker.validators import project_validation


@bp.route('/')
@login_required
def index():
    """Renders the dashboard template."""
    user_projects = current_user.user_projects
    return render_template(
        'dashboard/index.html', title='Dashboard', user_projects=user_projects
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
        role = Role.query.filter_by(name=role_name).first()

        data = role.id
        invited_user.add_notification('invitation', data, target_id=project.id)
        db.session.commit()

        return redirect(url_for('main.project', id=project.id))

    return render_template(
        'projects/project.html',
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
