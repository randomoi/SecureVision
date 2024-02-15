from app.forms.forms_user_profile import UpdateAccountForm
from flask_login import login_required, current_user
from app import db
from flask import url_for, redirect, Blueprint, flash, render_template, request, jsonify

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

blueprint_user = Blueprint('blueprint_user', __name__)

@blueprint_user.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UpdateAccountForm()
    
    # validates form on submission
    if form.validate_on_submit():
        made_updates = False
        attempted_password_change = False

        # updates user dinfo if changed
        if (current_user.first_name != form.first_name.data or 
            current_user.last_name != form.last_name.data or 
            current_user.email != form.email.data):
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            made_updates = True

        # checks for a password change 
        if form.current_password.data and form.password.data:
            attempted_password_change = True
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.password.data)
                made_updates = True
            else:
                flash('You entered incorrect current password.', 'danger')

        if made_updates:
            db.session.commit()
            flash('Your account was updated!', 'success')
        elif attempted_password_change:
            flash('No changes were made. You entered incorrect current password.', 'danger')
        else:
            flash('Changes were not detected.', 'info')

        return redirect(url_for('blueprint_user.user'))

    # on a GET request populates form fields with current user's info
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    return render_template('user_profile.html', title='Update Account', form=form)

@blueprint_user.route('/update_notifications', methods=['POST'])
@login_required
def update_notifications():
    new_notification_preference = request.form.get('preference')
    
    # check if new notification preference is valid 
    if new_notification_preference in ['all', 'hourly', 'none']:
        current_user.email_notification_preference = new_notification_preference  # updates user's notification preference
        db.session.commit()
        return jsonify({"message": "Updated notification preference."}), 200  # return successful response
    return jsonify({"message": "Invalid notification preference."}), 400  # return error response

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
# https://www.googlecloudcommunity.com/gc/Serverless/Forms-with-POST-method-not-working-properly-Google-App-Engine/m-p/621403?nobounce
# https://teamtreehouse.com/community/forms-tables-throwing-validation-error-solved
# https://flask-wtf.readthedocs.io/en/0.15.x/form/
# https://stackoverflow.com/questions/42018603/handling-get-and-post-in-same-flask-view
# https://community.postman.com/t/why-am-i-not-able-to-see-the-values-that-was-posted-in-form/52114
# https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """