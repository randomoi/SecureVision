from app.email_notifications.email_utilities import compose_and_send_email
from config import SENDER_EMAIL

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# constants 
EMAIL_SUBJECT_FOR_PASSWORD_RESET = "Password Reset"  
EMAIL_SUBJECT_PASSWORD_CHANGE_CONFIRMATION = "Password Change Confirmation"  
BASE_URL_FOR_PASSWORD_RESET = "http://127.0.0.1:5003/reset_password/"  
EMAIL_MESSAGE_TEMPLATE_FOR_PASSWORD_RESET = """
<p>A password reset was requested. Kindly access the provided hyperlink to initiate the process of resetting your password.</p>
<p>If you did not initiate a password reset, kindly disregard this email.</p>
<a href='{}'style="background-color: #800485; 
color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px; font-size: 14px;">Click Here</a>
"""



EMAIL_MESSAGE_TEMPLATE_FOR_PASSWORD_CHANGE_CONFIRMATION = """
<p>Your password was successfully changed. If you did not make this change, please contact customer service right away.</p>
"""

# send password reset email
def send_password_reset_email(user, reset_link):
    receiver_email = user.email  # retrieve email address 
    reset_url = BASE_URL_FOR_PASSWORD_RESET + reset_link  # create reset URL
    email_body = EMAIL_MESSAGE_TEMPLATE_FOR_PASSWORD_RESET.format(reset_url)  # create email body
    
    email_result = compose_and_send_email(SENDER_EMAIL, receiver_email, EMAIL_SUBJECT_FOR_PASSWORD_RESET, email_body)
    
    return email_result

# send password reset email confirmation
def send_change_of_password_confirmation_email(user):
    receiver_email = user.email  # retrieve email address 
    email_body = EMAIL_MESSAGE_TEMPLATE_FOR_PASSWORD_CHANGE_CONFIRMATION  # create email body
    
    email_result = compose_and_send_email(SENDER_EMAIL, receiver_email, EMAIL_SUBJECT_PASSWORD_CHANGE_CONFIRMATION, email_body)
    
    return email_result
 
# References:   
# https://forum.bubble.io/t/security-concern-send-password-reset-email-workflow-gives-away-whether-account-exists/63665
# https://stackoverflow.com/questions/21793829/how-to-make-django-password-reset-email-beautiful-html
# https://help.nextcloud.com/t/im-not-getting-an-e-mail-for-changing-password/79101
# https://community.auth0.com/t/password-reset-email-is-never-sent/107594
# https://forum.djangoproject.com/t/help-with-sending-password-resets/9807
# https://stackoverflow.com/questions/34279594/asp-net-identity-v2-0-0-email-confirmation-reset-password-errors
# https://community.auth0.com/t/problems-with-a-password-reset-link-email/76639
# https://github.com/supabase/gotrue-js/issues/342
# https://community.auth0.com/t/make-auth0-send-password-reset-email-or-welcome-email-when-user-is-created-thru-management-api/96778

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""