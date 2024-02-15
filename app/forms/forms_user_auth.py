from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class LoginForm(FlaskForm):
    # input field
    email = StringField('Email', validators=[DataRequired()])
    # input field
    password = PasswordField('Password', validators=[DataRequired()])
    # checkbox for remember me
    remember_me = BooleanField('Remember Me')  
    # submit button 
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    # input field
    first_name = StringField('First Name', validators=[DataRequired()])
    # input field
    last_name = StringField('Last Name', validators=[DataRequired()])
    # input field with email validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    # input field with validation 
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
    # submit button 
    submit = SubmitField('Register')

    # custom password validation
    def validate_password(self, field):
        if ' ' in field.data:
            raise ValidationError('Password should not contain spaces.')
        
class AdminLoginForm(FlaskForm):
    # input field with email validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    # input field
    password = PasswordField('Password', validators=[DataRequired()])
    # submit button 
    submit = SubmitField('Login')


# References: 
# https://flask.palletsprojects.com/en/2.3.x/patterns/wtforms/
# https://stackoverflow.com/questions/25324113/email-validation-from-wtform-using-flask
# https://snyk.io/advisor/python/WTForms/functions/wtforms.PasswordField
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms-2018/page/20
# https://wtforms.readthedocs.io/en/2.3.x/validators/
# https://www.geeksforgeeks.org/flask-wtf-explained-how-to-use-it/
# https://www.reddit.com/r/flask/comments/12ql63d/wtforms_problem_with_email_validation_equalto/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
""" 
