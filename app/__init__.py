from flask import Flask
from flask_session import Session
import os
from .views.views import UserModelView, MotionEventModelView, MotionSizeModelView, MotionPositionModelView, TokenModelView, GoogleDriveTokenModelView, ObjectTypeModelView, DetectedObjectModelView, MyAdminIndexView
from app.extensions.extensions import db, migrate, login_manager, csrf, admin
from flask_mail import Mail
from flask_apscheduler import APScheduler
from flask import g

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# sets environment variable for OAUTHLIB_INSECURE_TRANSPORT
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# # creates Mail instance without app context
# mail = Mail()

# create an APScheduler 
scheduler = APScheduler()

def create_app():
    # flask app instance
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # loads configuration settings 
    app.config.from_object('config')

    # init flask-wtf csrf protection
    csrf.init_app(app)

    # # init flask-mail with app context
    # mail.init_app(app)

    # checks session folder exists
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])

    # init flask-session extension
    Session(app)

    # register blueprints 
    from .routes.routes_general_app import main
    app.register_blueprint(main)

    from .routes.routes_user_profile_management import blueprint_user
    app.register_blueprint(blueprint_user)

    from .routes.routes_user_management import blueprint_user_authentication
    app.register_blueprint(blueprint_user_authentication)

    from .routes.routes_drive_auth_integration import blueprint_google_oauth2callback
    app.register_blueprint(blueprint_google_oauth2callback)

    from .routes.routes_admin_access import blueprint_admin_flask
    app.register_blueprint(blueprint_admin_flask)

    from .routes.routes_video_streaming_services import blueprint_streaming_services
    app.register_blueprint(blueprint_streaming_services)

    from .routes.routes_video_management import blueprint_video_management
    app.register_blueprint(blueprint_video_management)

    # init flask-sqlalchemy database
    db.init_app(app)
    # init flask-migrate
    migrate.init_app(app, db)
    # init flask-login
    login_manager.init_app(app)
    # init flask-csrf
    csrf.init_app(app)
    # init flask-admin with custom index to hide EMPTY home page
    admin.init_app(app, index_view=MyAdminIndexView())

    # sets login view for flask-login
    login_manager.login_view = 'blueprint_user_authentication.login'

    # adds views for flask-admin models
    from app.database_models.models import User, MotionEvent, MotionSize, Position, GmailToken, GoogleDriveToken, ObjectType, DetectedObject
    admin.add_view(UserModelView(User, db.session, endpoint='user'))
    admin.add_view(MotionEventModelView(MotionEvent, db.session))
    admin.add_view(ObjectTypeModelView(ObjectType, db.session))  
    admin.add_view(DetectedObjectModelView(DetectedObject, db.session))  
    admin.add_view(MotionSizeModelView(MotionSize, db.session))  
    admin.add_view(MotionPositionModelView(Position, db.session))  
    admin.add_view(TokenModelView(GmailToken, db.session))
    admin.add_view(GoogleDriveTokenModelView(GoogleDriveToken, db.session))

    # adds cli commands 
    from scripts.cli_commands import init_default_roles_command  
    app.cli.add_command(init_default_roles_command)

    from scripts.cli_commands import register_commands
    register_commands(app)

    # if setting up new db, make sure to comment this and func in scripts.setup before initializing db and creating tables, otherwise, it will rasie an error
    from scripts.setup import setup_roles
    setup_roles(app)

    # init and start flask-apscheduler to send hourly summaries
    scheduler.init_app(app)
    scheduler.start()
 
    from app.email_notifications.email_notifications_hourly import send_email_with_hourly_notifications_preference
    if not scheduler.get_job('send_email_with_hourly_notifications_preference'):
        scheduler.add_job(id='send_email_with_hourly_notifications_preference', func=send_email_with_hourly_notifications_preference, args=[app], trigger='interval', seconds=45)
    return app

# References:
# https://apscheduler.readthedocs.io/en/3.x/userguide.html
# https://www.pythonanywhere.com/forums/topic/13193/
# https://flask.palletsprojects.com/en/3.0.x/cli/
# https://stackoverflow.com/questions/61844593/admin-add-viewmodelviewuser-db-session-in-flask-admin-and-app-engine
# https://flask-migrate.readthedocs.io/en/latest/
# https://flask-login.readthedocs.io/en/latest/
# https://flask-wtf.readthedocs.io/en/0.15.x/csrf/
# https://github.com/flask-admin/flask-admin/blob/master/examples/auth-mongoengine/app.py
# https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
# https://www.python-engineer.com/posts/create-nested-directory/
# https://pythonhosted.org/Flask-Mail/
# https://testdriven.io/blog/csrf-flask/
# https://flask.palletsprojects.com/en/3.0.x/config/
# https://pypi.org/project/APScheduler/
# https://oauthlib.readthedocs.io/en/latest/oauth2/security.html
# https://flask.palletsprojects.com/en/2.3.x/logging/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""