from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

# Initialize SQLAlchemy for database management
db = SQLAlchemy()

# Initialize Migrate for database migrations
migrate = Migrate()

# Initialize LoginManager for user authentication
login_manager = LoginManager()

# Initialize CSRFProtect for CSRF protection in forms
csrf = CSRFProtect()

# Initialize Admin for the admin panel with Bootstrap 3 template
admin = Admin(name='My App Admin', template_mode='bootstrap3')


# References:
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/
# https://flask-migrate.readthedocs.io/en/latest/
# https://flask-login.readthedocs.io/en/latest/
# https://flask-wtf.readthedocs.io/en/0.15.x/csrf/
# https://flask-admin.readthedocs.io/en/latest/introduction/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """