from app.database_models.models import User
from app.forms.forms_user_auth import AdminLoginForm
from flask_login import login_user, current_user
from flask import url_for, redirect, Blueprint, flash, render_template, request
from functools import wraps

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

blueprint_admin_flask = Blueprint('blueprint_admin_flask', __name__)

@blueprint_admin_flask.route('/admin-login', methods=['GET', 'POST'])
def admin_login_flask_panel():
    # checks if current user is authenticated and has "admin" role
    if current_user.is_authenticated and current_user.has_role('admin'):
        return redirect(url_for('blueprint_admin_flask.admin_panel'))  # redirects to admin panel if already logged in as admin

    form = AdminLoginForm()  # create a admin login form 

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        # checks if user exists and password is correct
        if user and user.check_password(password):
            if user.has_role('admin'):
                login_user(user)  # login user
                return redirect(url_for('user.index_view'))  
            else:
                flash("Sorry, not you are authorized.", 'danger')  # flash a message for users who are not admin
                return redirect(url_for('blueprint_admin_flask.admin_login_flask_panel'))
        else:
            flash("Invalid email or password. Please try again.", 'danger')  # flash message for invalid credentials
            return redirect(url_for('blueprint_admin_flask.admin_login_flask_panel'))

    return render_template('admin_login.html', form=form)  # renders admin login page with form


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # checks if current user is anonymous or does not have admin role
        if current_user.is_anonymous or not current_user.has_role('admin'):
            return redirect(url_for('blueprint_admin_flask.admin_login_flask_panel'))  # redirects to admin login page if not authenticated as admin
        return f(*args, **kwargs)
    return decorated_function

@blueprint_admin_flask.route('/admin-panel')
@admin_required
def admin_panel():
    # redirects to user view instead of index view
    return redirect(url_for('user.index_view'))

# References:
# https://flask.palletsprojects.com/en/2.3.x/blueprints/
# https://realpython.com/flask-blueprint/
# https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://flask.palletsprojects.com/en/2.3.x/patterns/flashing/
# https://www.askpython.com/python-modules/flask/flask-flash-method
# https://stackoverflow.com/questions/74144214/python-decorator-check-if-user-is-admin
# https://flask-login.readthedocs.io/en/latest/
# https://flask-authorize.readthedocs.io/en/latest/usage.html
# https://flask-user.readthedocs.io/en/v0.5/authorization.html
# https://stackoverflow.com/questions/45890664/python-flask-user-login-redirection

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """