from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

class UserCustomForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_time_limit = timedelta(minutes=20)

    # fields for user details
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = StringField('Email')
    google_drive_enabled = BooleanField('Google Drive Enabled')
    
    # fields for selecting detection mode
    motion_detection_mode = SelectField('Detection Mode', choices=[
        ('mgo2', 'MGO2'),
        ('lucas_kanade_orb', 'lucas_kanade_orb'),
        ('mckenna', 'McKenna')
    ])
    
    # field for roles 
    roles = StringField('Roles')  
    
    # field for events 
    events = StringField('Events')  
    
    # fields for selecting notification preference
    email_notification_preference = SelectField('Notification Preference', choices=[
        ('all', 'All Notifications'),
        ('hourly', 'Hourly Notifications'),
        ('none', 'No Notifications')
    ])
    
# References:
# https://wtforms.readthedocs.io/en/2.3.x/csrf/
# https://gist.github.com/eddiecorrigall/ce0e475c9612ca750bcfb30cf108b763
# https://stackoverflow.com/questions/21501058/form-validation-fails-due-missing-csrf
# https://wtforms.readthedocs.io/_/downloads/en/2.2.x/pdf/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """