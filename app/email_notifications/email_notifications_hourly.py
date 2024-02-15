from app.database_models.models import User, MotionEvent
from app.email_notifications.email_utilities import compose_and_send_email
from datetime import datetime, timedelta
import logging
from config import SENDER_EMAIL, NA_OBJECT, NA_LOCATION, NA_SIZE, GREETING_TEMPLATE, BUTTON_TEMPLATE 
from app.email_notifications.video_email_link_handler import retrieve_video_link

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

# constants 
EMAIL_SUBJECT = "Motion detected (hourly notification mode)" 
ONE_HOUR = timedelta(hours=1) 
HTML_VIDEO_LINK_TEMPLATE = "<a href='{}' style={}</a>" 
HOURLY_NOTIFICATION_PREFERENCE = 'hourly' 
MOTION_EVENT_SUMMARY_TEMPLATE = "<li>Date/time: {timestamp} - Intruder position: {position} - Intruder size: {size} - Detected: {objects}. {button}</li>" 

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'  

# create HTML content for email 
def create_event_summaries_for_hourly_notifications(events):
    motion_event_summaries = []
    # finds detected objects, intruder postition, size etc
    for event in events:
        summary_of_detected_objects = ", ".join(obj.class_name for obj in event.detected_objects) if event.detected_objects else NA_OBJECT 
        position = event.position.name.lower() if event.position else NA_LOCATION
        motion_size = event.motion_size.size_name.lower() if event.motion_size else NA_SIZE
        
        # gets link for video       
        lint_to_video = retrieve_video_link(event)
        if lint_to_video != "There are no video available.":
            # adds styles within template 
            html_button = HTML_VIDEO_LINK_TEMPLATE.format(lint_to_video, BUTTON_TEMPLATE)
        else:
            html_button = lint_to_video  

        # use MOTION_EVENT_SUMMARY_TEMPLATE to format details of summaries
        event_summary = MOTION_EVENT_SUMMARY_TEMPLATE.format(
            timestamp=event.timestamp.strftime(DATE_TIME_FORMAT),
            position=position,
            size=motion_size,
            objects=summary_of_detected_objects,
            button=html_button
        )
        motion_event_summaries.append(event_summary)

    return f"<ul>{''.join(motion_event_summaries)}</ul>"


# sends hourly emails
def send_email_with_hourly_notifications_preference(app):
    one_hour_ago = datetime.utcnow() - ONE_HOUR
    # uses app contexct 
    with app.app_context():
        users = User.query.filter_by(email_notification_preference=HOURLY_NOTIFICATION_PREFERENCE).all()
        # queries information
        for user in users:
            events = MotionEvent.query.filter(
                MotionEvent.user_id == user.user_id,
                MotionEvent.timestamp > one_hour_ago
            ).all()

            if events:
                summary_of_events = create_event_summaries_for_hourly_notifications(events)
                email_greeting = GREETING_TEMPLATE.format(user.first_name)
                email_content = f"<html><body><h3>{email_greeting}</h3>The system detected the following motion events within past hour: {summary_of_events}</body></html>"
                # receivers email 
                receiver_email = user.email
               
                try: 
                    compose_and_send_email(SENDER_EMAIL, receiver_email, EMAIL_SUBJECT, email_content)
                except Exception as e:
                    logging.error(f"Error sending hourly emails: {e}")
            else:
                logging.info(f"There are no motion events {user.email} in the past hour.")

# References:
# https://medium.com/hacking-and-slacking/demystifying-flasks-application-context-c7bd31a53817
# https://stackoverflow.com/questions/73961938/flask-sqlalchemy-db-create-all-raises-runtimeerror-working-outside-of-applicat
# https://github.com/pytest-dev/pytest/issues/1395
# https://www.pythonanywhere.com/forums/topic/28656/
# https://www.reddit.com/r/learnpython/comments/10t3r4p/python_sqlalchemy_runtimeerror_working_outside_of/
# https://github.com/pallets/flask/issues/2900
# https://developer.android.com/reference/android/view/MotionEvent
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
