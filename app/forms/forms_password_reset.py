from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, ValidationError, StringField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError, Email
from app.database_models.models import User

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class ResetPasswordForm(FlaskForm):
    # input field with validators 
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])',
               message='The password must include at least one uppercase letter, one lowercase letter, one number, and one special character.')
    ])
    # input field with matching validation
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    # button for resetting password
    submit = SubmitField('Reset Password')

    # custom validation for spaces
    def validate_password(self, field):
        if ' ' in field.data:
            raise ValidationError('Password should not contain spaces.')

class ChangePasswordForm(FlaskForm):
    # input field
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    # input field with validators 
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])',
               message='The password must include at least one uppercase letter, one lowercase letter, one number, and one special character.')
    ])
    # input field with matching validation
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    # button for updating password
    submit = SubmitField('Update Password')

    # custom validation for spaces
    def validate_new_password(self, field):
        if ' ' in field.data:
            raise ValidationError('Password should not contain spaces.')
          
class RequestResetForm(FlaskForm):
    # input field with email validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    #  button for requesting password reset
    submit = SubmitField('Request Password Reset')

    # custom validation for email existing in db
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            print("Email does not exist!")
            raise ValidationError('No account with that email. Please register.')
        
# References:
# https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
# https://snyk.io/advisor/python/WTForms/functions/wtforms.PasswordField
# https://processwire.com/talk/topic/28522-frontend-validation-regex-for-username-and-password/
# https://stackoverflow.com/questions/73429532/problem-with-flask-wtforms-validation-errors
# https://elixirforum.com/t/groups-in-regex-to-validate-password/7086
# https://wtforms.readthedocs.io/en/2.3.x/validators/
# https://github.com/logaretm/vee-validate/issues/51

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""