"""Defines all wtf forms for projects blueprint.

  Typical usage example:

  form = InvitationForm()
  if form.validate_on_submit():
      pass
"""

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, ValidationError
from wtforms.validators import DataRequired, Email

from issue_tracker.models import User


class InvitationForm(FlaskForm):
    email = StringField(
        'Invite a new member to your project',
        validators=[
            DataRequired(message='Please enter an email address.'),
            Email(message='Please enter a valid email address.'),
        ],
    )
    role = SelectField(
        'role', choices=[('Reviewer', 'Reviewer'), ('Developer', 'Developer')]
    )

    def __init__(self, user_projects, *args, **kwargs):
        super(InvitationForm, self).__init__(*args, **kwargs)
        self.user_projects = user_projects

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()

        if not self.email.errors:
            if not user:
                raise ValidationError('Unknown email address. Please try again.')
            elif email == current_user.email:
                raise ValidationError('You can not invite yourself to your project.')
            elif self.user_projects.filter_by(user=user).first():
                raise ValidationError('User is already a member of the project.')
