from app.__init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime
from dotenv import load_dotenv
import os

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# loads environment variables from the .env file
# https://pypi.org/project/python-dotenv/
# https://www.python-engineer.com/posts/dotenv-python/
load_dotenv()

serializer_token_secret = os.environ.get('SERIALIZER_TOKEN_SECRET', 'default_fallback_secret')
print("serializer_token_secret:", serializer_token_secret)

# creates a URLSafeTimedSerializer instance using serializer_token_secret
# https://itsdangerous.palletsprojects.com/en/2.1.x/url_safe/
s = URLSafeTimedSerializer(serializer_token_secret)

# defines many-to-many association table for roles and users
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.role_id'), primary_key=True)
)


class Role(db.Model):
    # primary key 
    role_id = db.Column(db.Integer(), primary_key=True)
    
    # unique name 
    name = db.Column(db.String(80), unique=True)
    
    def __repr__(self):
        # eturns a string 
        return '<Role %r>' % self.name

class User(db.Model, UserMixin):
    # primary key 
    user_id = db.Column(db.Integer, primary_key=True)
    
    # first name of user
    first_name = db.Column(db.String(100), nullable=False)
    
    # last name of user
    last_name = db.Column(db.String(100), nullable=False)
    
    # email of user its unique and indexed
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    
    # password hash for securely storing password
    password_hash = db.Column(db.String(255), nullable=False)  
    
    # relationship 
    events = db.relationship('MotionEvent', back_populates='user', cascade="all, delete-orphan")
    
    # relationship 
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    
    # enable Google Drive with false default
    google_drive_enabled = db.Column(db.Boolean, default=False, nullable=True)
    
    # notification preference ("all", "hourly", "none")
    email_notification_preference = db.Column(db.String(10), default='all', nullable=False)
    
    # motion_detection_mode 
    motion_detection_mode = db.Column(db.String(50), nullable=True)

    # token expiration 
    expires_sec = 1800 
    
    # sets password hash 
    def set_password(self, password):
        self.password_hash = generate_password_hash(password) 

    # checks if provided password matches the stored password hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  
    
    # checks if user is active
    @property
    def is_active(self):
        return True
    # gets user ID as string
    def get_id(self):
        return str(self.user_id)

    # returns string representation
    def __repr__(self):
        return f'<User {self.email}>'
    
    # checks if user has a role
    def has_role(self, role_name):
        return any([role.name == role_name for role in self.roles])
    
    # generates reset token for password reset
    @classmethod
    def get_reset_token(cls, user_id):
        return s.dumps({"user_id": user_id}, salt='reset-password')

    # verifies and decodes password reset token
    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = s.loads(token, salt='reset-password', max_age=User.expires_sec)['user_id']
        except SignatureExpired:
            return None
        return User.query.get(user_id)


class MotionSize(db.Model):
    # primary key 
    size_id = db.Column(db.Integer, primary_key=True)
    
    # name of intruder size 
    size_name = db.Column(db.String(100), nullable=False, unique=True)
    
    # relationship 
    events = db.relationship('MotionEvent', back_populates='motion_size')
    
    #  returns string representation 
    def __repr__(self):
        return f'<MotionSize {self.size_name}>'

class Position(db.Model):
    # primary key 
    position_id = db.Column(db.Integer, primary_key=True)
    
    # position name 
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # relationship
    events = db.relationship('MotionEvent', back_populates='position')

    #  returns string representation 
    def __repr__(self):
        return f'<Position {self.name}>'

class ObjectType(db.Model):
    # primary key 
    object_type_id = db.Column(db.Integer, primary_key=True)
    
    # object name 
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        #  returns string representation 
        return f'<ObjectType {self.name}>'

class MotionEvent(db.Model):
    # primary key 
    event_id = db.Column(db.Integer, primary_key=True)
    
    # timestamp for when motion event happened
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # foreign key to connect with Position table
    position_id = db.Column(db.Integer, db.ForeignKey('position.position_id'))
    
    # foreign key to connect with Intruder size table
    size_id = db.Column(db.Integer, db.ForeignKey('motion_size.size_id'))
    
    # path to recorded video 
    video_path = db.Column(db.String(1024), nullable=True)
    
    # foreign key to connect with a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
    # relationship to access related Position
    position = db.relationship('Position', back_populates='events')
    
    # relationship to access related MotionSize
    motion_size = db.relationship('MotionSize', back_populates='events')
    
    # relationship to access related DetectedObjects (has cascade delete)
    detected_objects = db.relationship('DetectedObject', backref='motion_event', lazy=True, cascade="all, delete-orphan")
    
    # relationship to access related User
    user = db.relationship('User', back_populates='events')
    
    # google drive file ID
    google_drive_file_id = db.Column(db.String(255), nullable=True)
    
    # path to motion-detected image 
    image_path = db.Column(db.String(1024), nullable=True)

    #  returns string representation 
    def __repr__(self):
        return f'<MotionEvent {self.event_id} for User {self.user_id}>'


class DetectedObject(db.Model):
    # primary key 
    detected_object_id = db.Column(db.Integer, primary_key=True)
    
    # foreign key to connect with MotionEvent table
    motion_event_id = db.Column(db.Integer, db.ForeignKey('motion_event.event_id'))
    
    # name of detected object
    class_name = db.Column(db.String(255))
    
    #  score of detection
    score = db.Column(db.Float)
    
    # foreign key to connect with ObjectType table
    object_type_id = db.Column(db.Integer, db.ForeignKey('object_type.object_type_id'))
    
    # relationship to access related ObjectType
    object_type = db.relationship('ObjectType', backref='detected_objects')
    
    # relationship to access parent MotionEvent
    detected_objects_in_event = db.relationship('MotionEvent', back_populates='detected_objects')

    #  returns string representation 
    def __repr__(self):
        return f'<DetectedObject {self.detected_object_id} class_name={self.class_name} score={self.score} object_type_id={self.object_type_id}>'

class GmailToken(db.Model):
    # primary key 
    token_id = db.Column(db.Integer, primary_key=True)
    
    # access token
    access_token = db.Column(db.String(255), nullable=False)
    
    # refresh token
    refresh_token = db.Column(db.String(255), nullable=False)
    
    # token expiration 
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # token type
    token_type = db.Column(db.String(50), nullable=False)

    # saves token to db
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # gets stored tokens from db
    @classmethod
    def get_tokens(cls):
        return cls.query.first()  


class GoogleDriveToken(db.Model):
    # primary key 
    google_drive_token_id = db.Column(db.Integer, primary_key=True)
    
    # access token 
    access_token = db.Column(db.String(255), nullable=False)
    
    # refresh token
    refresh_token = db.Column(db.String(255), nullable=True)
    
    # token expiration
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # user id associated with this token 
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    # saves tokens to db
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # gets most recent token for user
    @classmethod
    def get_token_for_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.google_drive_token_id.desc()).first()

 
# References:
# https://gist.github.com/mjhea0/9b9c400a2bc58e6c90e5f77eeb739d6b
# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#adding-and-updating-objects
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#querying
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#rolling-back
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#querying-with-joins
# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#deleting
# https://docs.sqlalchemy.org/en/13/orm/relationships.html
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#one-to-many
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object
# https://docs.sqlalchemy.org/en/13/orm/index.html
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html
# https://docs.sqlalchemy.org/en/20/core/reflection.html
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxiii-application-programming-interfaces-apis/page/7
# https://stackoverflow.com/questions/18110033/getting-first-row-from-sqlalchemy
# https://elixirforum.com/t/referencing-a-table-through-a-composite-foreign-key-throws-column-id-does-not-exist/52041
# https://forum.djangoproject.com/t/incompatible-foreign-key-when-attempting-to-link-tables-in-django/14650
# https://stackoverflow.com/questions/1984162/purpose-of-repr-method
# https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
# https://docs.sqlalchemy.org/en/20/orm/cascades.html
# https://flask-scrypt.readthedocs.io/en/latest/
# https://sqlalchemy-utils.readthedocs.io/en/latest/_modules/sqlalchemy_utils/types/password.html
# https://sqlalchemy-filters-plus.readthedocs.io/en/latest/guide/nested_filters.html
# https://snyk.io/advisor/python/itsdangerous/functions/itsdangerous.SignatureExpired
# https://tedboy.github.io/flask/generated/werkzeug.check_password_hash.html
# https://www.gitauharrison.com/articles/apis-in-flask/authentication
# https://tedboy.github.io/flask/generated/werkzeug.generate_password_hash.html
# https://paduck210.github.io/flask/flask-password-hashing-IMPORTANT/
# https://dev.to/goke/securing-your-flask-application-hashing-passwords-tutorial-2f0p
# https://teamtreehouse.com/community/checkpasswordhash-with-flaskbcrypt
# https://docs.sqlalchemy.org/en/20/orm/backref.html
# https://teamtreehouse.com/library/a-social-network-with-flask/the-usermixin-from-flasklogin
# https://itsdangerous.palletsprojects.com/en/2.1.x/url_safe/
# https://pypi.org/project/python-dotenv/
# https://www.python-engineer.com/posts/dotenv-python/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""