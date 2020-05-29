from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, Email

from issue_tracker.models import User


class InvitationForm(FlaskForm):
    email = StringField('Invite a new member', validators=[DataRequired(), Email()])

    def validate_email(self, field):
        # Raise a ValidationError if email is valid, but doesn't belong to any user.
        if not self.email.errors and not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown email address. Please try again.')
