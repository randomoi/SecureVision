
import os
from datetime import timedelta

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) 

AUTH_SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/drive.file']

GOOGLE_CLIENT_ID = '969051066749-eu4idc9ac8sb0e9951ppknebhp6vuanj.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'

# sets path for CLIENT_SECRETS_FILE relative to BASE_DIRECTORY
CLIENT_SECRETS_FILE = os.path.join(BASE_DIRECTORY, 'client_secret', 'client_secret_969051066749-eu4idc9ac8sb0e9951ppknebhp6vuanj.apps.googleusercontent.com.json')

# secret key is required for secure flask sessions
SECRET_KEY = b'2cac5a5f136559a72bbb32a8438b494e0e890b27dd8df4006427dd4323f1015f'

# constants
OAUTH2_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
REFRESH_TOKEN_TYPE = 'refresh_token'
TOKEN_EXPIRATION_BUFFER_IN_SECONDS = 60  
GMAIL_API_SEND_URL = "https://www.googleapis.com/gmail/v1/users/me/messages/send"
SENDER_EMAIL = "Security System <sender.demo2020@gmail.com>" 
GREETING_TEMPLATE = "<p>Dear {},</p>" 
BUTTON_TEMPLATE = "<a href='{}' style='background-color: #0897a1; color: white; padding: 8px 18px; text-align: center; text-decoration: none; display: inline-block; font-size: 15px; margin: 3px 2px; cursor: pointer;'>Video Link</a>" 
NA_OBJECT  = "n/a object"
NA_LOCATION = "n/a location"
NA_SIZE = "n/a size"


VIDEO_DIRECTORY = os.path.join(BASE_DIRECTORY, 'app', 'static', 'videos')
if not os.path.exists(VIDEO_DIRECTORY):
    os.makedirs(VIDEO_DIRECTORY)

PATH_FOR_SAVING_IMAGE = os.path.join(BASE_DIRECTORY, 'app', 'static', 'images')

if not os.path.exists(PATH_FOR_SAVING_IMAGE):
    os.makedirs(PATH_FOR_SAVING_IMAGE)

PATH_FOR_SAVING_PROCESSED_IMAGE = os.path.join(BASE_DIRECTORY, 'app', 'static', 'processed_images')

if not os.path.exists(PATH_FOR_SAVING_PROCESSED_IMAGE):
    os.makedirs(PATH_FOR_SAVING_PROCESSED_IMAGE)
    
# database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIRECTORY, 'db', 'motion.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# flask session configuration
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'flask_session')
SESSION_FILE_THRESHOLD = 500
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'motion_'

# flask-login configuration 
REMEMBER_COOKIE_DURATION = timedelta(days=30) 
REMEMBER_COOKIE_SECURE = True 
REMEMBER_COOKIE_HTTPONLY = True  

# detects environment based on environment variable 
ENVIRONMENT = os.environ.get('FLASK_ENV', 'development')

# development configuration
if ENVIRONMENT == 'development':
    SERVER_NAME = '127.0.0.1:5003'
else:
    SERVER_NAME = 'some_example.com'

# References:
# https://flask-login.readthedocs.io/en/latest/
# https://flask-login.readthedocs.io/_/downloads/en/0.4.1/pdf/
# https://flask-session.readthedocs.io/en/latest/config.html
# https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application
# https://stackoverflow.com/questions/72791483/should-i-use-os-path-exists-before-os-makedirs
# https://note.nkmk.me/en/python-os-mkdir-makedirs/
# https://developers.google.com/gmail/api/auth/scopes
# https://flask.palletsprojects.com/en/1.1.x/config/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""