from app.database_models.models import User
from flask_wtf.csrf import generate_csrf
from flask_login import login_required, current_user
from app import login_manager
from flask import url_for, redirect, Blueprint, render_template, session

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

main = Blueprint('main', __name__)

@main.route('/setup_guide')
def setup_guide():
    # renders page
    return render_template('project_setup_guide.html')

@main.route('/completed_setup_guide')
def completed_setup_guide():
    # sets the flag to True 
    session['completed_setup'] = True
    # redirects to registration page
    return redirect(url_for('blueprint_user_authentication.register'))

@main.route('/')
def index():
    # checks if flag is present 
    completed_setup = session.get('completed_setup', False)
  
    if not completed_setup:
        # if not completed, redirects to the setup guide
        return redirect(url_for('main.setup_guide'))

    # if user is authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        # otherwise, redirect to login page
        return redirect(url_for('blueprint_user_authentication.login'))

@login_manager.user_loader
def load_user(user_id):
    # load User object from db based on user_id
    return User.query.get(int(user_id))


@main.route('/questions_and_answers')
@login_required 
def questions_and_answers():
    # generates CSRF token for route
    csrf_token = generate_csrf()
    return render_template('questions_and_answers.html', csrf_token=csrf_token, load_css_styles=True)

@main.route('/legal_disclaimers')
@login_required 
def legal_disclaimers():
    # generates CSRF token for route
    csrf_token = generate_csrf()
    return render_template('legal_disclaimers.html', csrf_token=csrf_token, load_css_styles=True)

@main.route('/dashboard')
@login_required  
def dashboard():
    # generates CSRF token for route
    csrf_token = generate_csrf()
    # gets user's detection mode, defaults to 'mgo2' if not set
    user_detection_mode = current_user.motion_detection_mode if current_user.motion_detection_mode else 'mgo2'
    return render_template('dashboard.html', csrf_token=csrf_token, user_detection_mode=user_detection_mode, load_css_styles=True)

# References:
# https://flask-wtf.readthedocs.io/en/0.15.x/api/
# https://gist.github.com/frostming/dbb514c8ae1e9363039e9df537988812
# https://geekpython.in/structure-flask-app-with-blueprint
# https://flask.palletsprojects.com/en/2.3.x/blueprints/
# https://realpython.com/flask-blueprint/
# https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://flask-authorize.readthedocs.io/en/latest/usage.html
# https://community.render.com/t/csrf-token-not-working-in-flask-app/18197
# https://github.com/oauth2-proxy/oauth2-proxy/issues/817
# https://www.freecodecamp.org/news/how-to-authenticate-users-in-flask/
# https://flask-login.readthedocs.io/en/latest/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """