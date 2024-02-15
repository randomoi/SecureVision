from app.database_models.models import User, MotionEvent
from app.email_notifications.email_utilities import compose_and_send_email
from app.email_notifications.email_token import retrieve_access_token
from config import SENDER_EMAIL, NA_OBJECT, NA_LOCATION, NA_SIZE, GREETING_TEMPLATE, BUTTON_TEMPLATE 
from app.email_notifications.video_email_link_handler import retrieve_video_link, no_video_available
import logging

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """


# defind constants 
EMAIL_SUBJECT = "Motion detected (all notification mode)" 
NO_RECENT_EVENTS_HTML = "<p>No recent motion events.</p>" 
ALL_EMAIL_CONTENT_TEMPLATE = "<p>The system detected motion in the {}. It is a {}. It is a {}.</p>" 
DEFAULT_USER_NAME = "User"

# error messages
ERROR_ACCESS_TOKEN_NOT_FOUND = "Could not retrieve access token."
USER_NOT_FOUND_ERROR = "User was not found."
NO_EVENTS = "No recent motion events."

# create HTML content for email 
def create_email_content_for_all_notifications(user, latest_motion_event):
    user_name = f"{user.first_name} {user.last_name}" if user else DEFAULT_USER_NAME
    email_greeting = GREETING_TEMPLATE.format(user_name)
    
    # finds detected object, intruder position and size, link etc in the last motion event
    if latest_motion_event:
        summary_of_detected_objects = ", ".join(obj.class_name for obj in latest_motion_event.detected_objects) if latest_motion_event.detected_objects else NA_OBJECT 
        position = latest_motion_event.position.name.lower() if latest_motion_event.position else NA_LOCATION
        motion_size = latest_motion_event.motion_size.size_name.lower() if latest_motion_event.motion_size else NA_SIZE
        motion_event_metadata = ALL_EMAIL_CONTENT_TEMPLATE.format(position, motion_size, summary_of_detected_objects)
        link_to_video = retrieve_video_link(latest_motion_event)
        html_video_link = BUTTON_TEMPLATE.format(link_to_video) if link_to_video else no_video_available()
    else: # if nothing found 
        motion_event_metadata = NO_RECENT_EVENTS_HTML
        html_video_link = ""

    motion_event_information = f"{email_greeting}{motion_event_metadata}{html_video_link}"
    return f"<html><body>{motion_event_information}</body></html>"


# sends email to user who has preference for all notifications
def send_email_with_preference_for_all_notifications(app, receiver_email, message_text, image_path=None):
    access_token = retrieve_access_token()
    # checks for valid token
    if not access_token:
        logging.error(ERROR_ACCESS_TOKEN_NOT_FOUND)
        return "Could not send email. " + ERROR_ACCESS_TOKEN_NOT_FOUND
    # uses app context
    with app.app_context():
        try:
            user = User.query.filter_by(email=receiver_email).first()
            if not user:
                return USER_NOT_FOUND_ERROR
            
            # queries for latest motion event
            latest_motion_event = MotionEvent.query.filter_by(user_id=user.user_id).order_by(MotionEvent.timestamp.desc()).first()
            
            # if not found returns message
            if not latest_motion_event:
                return NO_EVENTS

            entire_message = create_email_content_for_all_notifications(user, latest_motion_event)
            paths_to_files = [image_path] if image_path else None
            email_content = compose_and_send_email(SENDER_EMAIL, receiver_email, EMAIL_SUBJECT, entire_message, paths_to_files, "image")
        except Exception as e:
            return f"Error! Error when sending email: {e}"

# References:
# https://stackoverflow.com/questions/77483917/scopes-confusion-using-smtp-to-send-email-using-my-gmail-account-with-xoauth2
# https://flask.palletsprojects.com/en/2.3.x/appcontext/
# https://mailtrap.io/blog/python-send-html-email/
# https://stackoverflow.com/questions/882712/send-html-emails-with-python
# https://towardsdatascience.com/how-to-distribute-your-data-reports-via-mail-with-a-few-lines-of-code-8df395c72e55
# https://www.justintodata.com/send-email-using-python-tutorial/
# https://docs.python.org/3/library/email.examples.html
# https://stackoverflow.com/questions/6706891/embedding-image-in-html-email
# https://developer.android.com/reference/android/view/MotionEvent

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """
