from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from issue_tracker.dashboard import bp
from issue_tracker.models import db, Project


@bp.route('/dashboard')
@login_required
def dashboard():
    projects = current_user.projects.all()
    return render_template('dashboard.html', title='Dashboard', projects=projects)


@bp.route('/projects', methods=['POST'])
@login_required
def projects():
    project_count = current_user.projects.count()
    if project_count == 4:
        flash(
            'You can not add any more projects, you can only create 4 or less projects.'
            'Please delete one existing project before you add any more.'
        )
        return redirect(url_for('index'))

    title = request.form['title']
    description = request.form['description']
    print(title, description)

    project = Project(title=title, description=description)
    current_user.projects.append(project)
    db.session.commit()
    return redirect(url_for('index'))
