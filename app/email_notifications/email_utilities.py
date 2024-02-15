import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import requests
from app.email_notifications.email_token import retrieve_access_token
from config import GMAIL_API_SEND_URL

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# constants
MIME_TYPE_HTML = "html"
RESPONSE_CODE_SUCCESS = 200
CONTENT_TYPE = "application/json"
AUTHORIZATION_PREFIX = "Bearer "
HEADER_ACCEPT = "application/json"
ERROR_TOKEN_MESSAGE = "Did not retrieve access token. Email was not sent."
SUCCESS_MESSAGE = "Email was sent."
ERROR_EMAIL_MESSAGE = "Did not send email. Response:"
JPEG_MIME = "jpeg"
IMG_CONTENT_ID = "<image1>"

logging.basicConfig(level=logging.INFO)

# creates a base MIME Multipart email 
def create_mime_multipart_email(sender, to, subject):
    message = MIMEMultipart("related")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    return message

# attaches HTML body to the message
def attach_html_body_to_mime_multipart_email(message, body):
    message.attach(MIMEText(body, MIME_TYPE_HTML))

# attaches file to the message
def attach_file_to_mime_multipart_email(message, file_path, file_type="image"):
    if file_type == "image":
        with open(file_path, 'rb') as file:
            file_content = file.read()
            msg_image = MIMEImage(file_content, _subtype=JPEG_MIME)
            msg_image.add_header("Content-ID", IMG_CONTENT_ID)
            message.attach(msg_image)

# encodes MIME message to base64 URL format then returns dictionary
def encode_mime_multipart_message(message):
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

# sends email using gmail API
def send_email_using_gmail_api(email_content):
    # retrieves access token 
    access_token = retrieve_access_token()
    
    # checks if access token was retrieved
    if not access_token:
        return ERROR_TOKEN_MESSAGE

    # creates headers needed for Gmail API request
    headers = {
        "Authorization": f"{AUTHORIZATION_PREFIX}{access_token}",
        "Accept": HEADER_ACCEPT,
        "Content-Type": CONTENT_TYPE
    }
    
    # sends the email using Gmail API
    response = requests.post(GMAIL_API_SEND_URL, headers=headers, json=email_content)
    
    # checks if the email was sent based on response code
    if response.status_code == RESPONSE_CODE_SUCCESS:
        logging.info(SUCCESS_MESSAGE)
        return SUCCESS_MESSAGE
    else: # otherewise returns error
        error_message = f"{ERROR_EMAIL_MESSAGE} {response.text}"
        logging.error(error_message)
        return error_message

# composes email with needed attachements and sends it
def compose_and_send_email(sender, receiver, subject, body, file_paths=None, file_type="image"):
    # creates mime multipart email message
    message = create_mime_multipart_email(sender, receiver, subject)
    
    # attaches body to the email
    attach_html_body_to_mime_multipart_email(message, body)
    
    # attaches needed files, if any
    if file_paths:
        for file_path in file_paths:
            attach_file_to_mime_multipart_email(message, file_path, file_type)
    
    # encodes email message
    email_content = encode_mime_multipart_message(message)
    
    # send email and returns result
    return send_email_using_gmail_api(email_content)

# References:
# https://mailtrap.io/blog/python-send-email-gmail/
# https://mailtrap.io/blog/send-emails-with-gmail-api/
# https://developers.google.com/gmail/api/auth/web-server
# https://community.retool.com/t/issues-in-sending-gmail/31618
# https://en.delphipraxis.net/topic/1949-sending-email-via-gmail-using-oauth-20-via-indy/
# https://stackoverflow.com/questions/52292971/sending-single-email-with-3-different-attachments-python-3
# https://powerusers.microsoft.com/t5/Building-Flows/Sending-an-email-with-multiple-attachments-based-on-conditions/td-p/444855
# https://gist.github.com/haccks/4c8d73fbd9fa202c720de9a3c9011483
# https://blog.lordvan.com/blog/sending-multipart-mime-emails-html-text-alternative-using-python-and-twisted/
# https://docs.python.org/3/library/email.mime.html
# https://gist.github.com/turicas/1455741?permalink_comment_id=1976893
# https://community.esri.com/t5/geoprocessing-questions/change-smtp-to-html-in-reconcilecompress-script/td-p/418047
# https://docs.activestate.com/activepython/2.7/python/library/email-examples.html
# https://stackoverflow.com/questions/41280607/how-do-i-attach-html-in-email-body-using-python
# https://stackoverflow.com/questions/74953960/send-email-with-plain-text-and-html-attachment
# https://stackoverflow.com/questions/42599590/cant-find-file-to-send-file-as-attachment-in-python
# https://forum.asana.com/t/how-to-upload-attachment-using-python-api/103506
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
# https://python.hotexamples.com/examples/email.mime.multipart/MIMEBase/-/python-mimebase-class-examples.html
# https://github.com/googleapis/google-api-python-client/issues/243
# https://docs.python.org/3/library/base64.html
# https://www.php.net/manual/en/function.base64-encode.php
# https://developer.mozilla.org/en-US/docs/Glossary/Base64

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""