from app.database_models.models import User, Role, User
from app.forms.forms_user_auth import LoginForm, RegistrationForm
from app.forms.forms_password_reset import ChangePasswordForm, ResetPasswordForm, RequestResetForm
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from flask import url_for, redirect, Blueprint, flash, render_template, request, jsonify
from app.email_notifications.password_reset_notifications import send_password_reset_email, send_change_of_password_confirmation_email  

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

blueprint_user_authentication = Blueprint('blueprint_user_authentication', __name__)

@blueprint_user_authentication.route('/register', methods=['GET', 'POST'])
def register():
    # checks if user is authenticated and redirects to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()  # creates registration form 

    if form.validate_on_submit():
        # gets user registration data 
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        # check if email already exists in db
        existing_user_email = User.query.filter_by(email=email).first()
        if existing_user_email:
            # flash error message 
            flash(f"Email already registered!", 'danger')
            return redirect(url_for('blueprint_user_authentication.register'))  # redirects back to registration page

        # creates a new user instance with the provided info
        user_new = User(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user_new.set_password(password)  # sets password securely

        # assigns default role (user)
        default_role = Role.query.filter_by(name="user").first() 
        if default_role:
            user_new.roles.append(default_role)

        db.session.add(user_new)
        db.session.commit()

        # flash success message and redirect to login page
        flash("You successfully registered.", "success")
        return redirect(url_for('blueprint_user_authentication.login'))

    # renders registration form template
    return render_template('register.html', form=form)


@blueprint_user_authentication.route('/login', methods=['GET', 'POST'])
def login():
    # checks if user is authenticated and redirects to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()  # Cceates login form 

    if form.validate_on_submit():
        # queries db to find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # checks if user exists and password is correct
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'danger')  # flash error message in creds invalid

    # renders login form template
    return render_template('login.html', form=form)


@blueprint_user_authentication.route('/logout')
@login_required
def logout():
    logout_user()  # log out current user
    return render_template('logout.html')  # renders logout page


@blueprint_user_authentication.route("/reset_password", methods=['GET', 'POST'])
def reset_password_request():
    # checks if user is already authenticated and redirects to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RequestResetForm()  # creates request reset form 
    
    if form.validate_on_submit():
        # queries db to find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # gets reset token and send a reset email to  user
            token = User.get_reset_token(user.user_id)
            send_password_reset_email(user, token)
            flash('Email was sent with reset password instructions.', 'info')
            return redirect(url_for('blueprint_user_authentication.login'))  # redirects to login page
        else:
            flash('There is no account with that email. You must register first.', 'warning')
    
    return render_template('password_reset_request.html', title='Reset Password', form=form)

@blueprint_user_authentication.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # checks if user is already authenticated 
    if current_user.is_authenticated:
        return redirect(url_for('blueprint_user_authentication.change_password'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('Used invalid or expired token.', 'warning')
        return redirect(url_for('blueprint_user_authentication.reset_password_request'))  # redirects to password reset request page

    form = ResetPasswordForm()  # creates password reset form
    
    if form.validate_on_submit():
        user.set_password(form.password.data)  # update user's password
        db.session.commit()
        flash('Your password has been updated!', 'success')

        # sends password change confirmation email
        send_change_of_password_confirmation_email(user)

        return redirect(url_for('blueprint_user_authentication.login'))  # redirects to login page
    
    return render_template('password_reset_token.html', title='Reset Password', form=form, token=token)


@blueprint_user_authentication.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()  # creates change password form
    source = request.form.get('source')  # gets source of request

    if form.validate_on_submit():
        user = current_user
        if user.check_password(form.current_password.data):
            user.set_password(form.new_password.data)  # set new password for user
            db.session.commit()
            flash('Your password was updated!', 'success')

            # redirects based on source of password change request
            if source == 'profile':
                return redirect(url_for('main.user'))  # redirects to user profile page
            else:
                return redirect(url_for('main.dashboard'))  # redirects to dashboard
        else:
            flash('Invalid current password. Please try again.', 'danger')  # flash error message if current password is incorrect

    return render_template('password_change.html', title='Change Password', form=form)


@blueprint_user_authentication.route('/validate-current-password', methods=['POST'])
@login_required
def validate_current_password():
    current_password = request.form.get('current_password')
    # checks if current password matches user's stored password
    if current_user.check_password(current_password):
        return jsonify({'is_correct': True})  # returns JSON response saying password is correct
    else:
        return jsonify({'error': 'Current password is incorrect! Please try again.'}), 400  # returns error response if password is incorrect

# References:
# https://stackoverflow.com/questions/77370756/do-i-need-to-verify-a-login-request-is-post-when-im-using-request-form-get
# https://flask-login.readthedocs.io/en/latest/
# https://medium.com/hacking-and-slacking/handle-user-accounts-authentication-in-flask-with-flask-login-944cc065b7f2
# https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
# https://stackoverflow.com/questions/68395618/change-password-form-not-working-in-flask
# https://flask-security-too.readthedocs.io/en/stable/customizing.html
# https://flask-security-too.readthedocs.io/en/stable/customizing.html#customizing-the-login-form
# https://flask-security-too.readthedocs.io/en/stable/customizing.html#controlling-form-instantiation
# https://flask-security-too.readthedocs.io/en/stable/customizing.html#json-response
# https://stackoverflow.com/questions/77477466/my-reset-password-link-for-my-flask-web-app-is-not-redirecting-and-updating-the
# https://flask-wtf.readthedocs.io/en/0.15.x/quickstart/
# https://flask-wtf.readthedocs.io/en/0.15.x/quickstart/#validating-forms
# https://flask-wtf.readthedocs.io/en/0.15.x/quickstart/#creating-forms
# https://stackoverflow.com/questions/43002323/difference-between-form-validate-on-submit-and-form-validate
# https://tedboy.github.io/flask/generated/werkzeug.check_password_hash.html
# https://python-commandments.org/flask-authentication/
# https://nrodrig1.medium.com/flask-mail-reset-password-with-token-8088119e015b#:~:text=get_reset_token()%20is%20a%20method,the%20body%20of%20an%20email.
# https://ryansblog2718281.medium.com/flask-login-and-is-authenticated-94bdb0aecd46
# https://hackersandslackers.com/flask-login-user-authentication/
# https://flask.palletsprojects.com/en/2.3.x/blueprints/
# https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """