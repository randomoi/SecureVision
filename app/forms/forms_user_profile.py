from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError, Optional
from flask_login import current_user

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class UpdateAccountForm(FlaskForm):
    # input field with length validation
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    # input field with length validation
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    # input field with email validation
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    #  input field
    current_password = PasswordField('Current Password', validators=[
        DataRequired()
    ])
   # input field with optional validators for length/complexity
    password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=8),
        Regexp(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])',
               message='The password must include at least one uppercase letter, one lowercase letter, one number, and one special character.')
    ])
    # input field with matching validation
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(),
        EqualTo('password', message='Passwords must match.')
    ])

    # submit button 
    submit = SubmitField('Update')
    
    # custom validation for spaces
    def validate_password(self, field):
        if ' ' in field.data:
            raise ValidationError('Password should not contain spaces.')
       
    # custom validation for current password correctess
    def validate_current_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Current password is incorrect.')

# References: 
# https://flask.palletsprojects.com/en/2.3.x/patterns/wtforms/
# https://stackoverflow.com/questions/25324113/email-validation-from-wtform-using-flask
# https://snyk.io/advisor/python/WTForms/functions/wtforms.PasswordField
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms-2018/page/20
# https://wtforms.readthedocs.io/en/2.3.x/validators/
# https://www.geeksforgeeks.org/flask-wtf-explained-how-to-use-it/
# https://www.reddit.com/r/flask/comments/12ql63d/wtforms_problem_with_email_validation_equalto/
# https://stackoverflow.com/questions/73765342/trouble-with-flask-wtforms-validators-forms-inside-of-form
# https://wtforms.readthedocs.io/en/3.0.x/validators/
# https://github.com/wtforms/flask-wtf/issues/218
# https://medium.com/hacking-and-slacking/handling-forms-in-flask-with-flask-wtf-167b76f2d6d3

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""