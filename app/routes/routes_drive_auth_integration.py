import google_auth_oauthlib.flow
from config import CLIENT_SECRETS_FILE, AUTH_SCOPES
from flask import url_for, session, current_app, jsonify, request, Blueprint, redirect
from flask_login import current_user
from app.database_models.models import User
from app.google_drive.drive_token_services import save_google_drive_credentials, convert_credentials_to_dict
from app import db

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

blueprint_google_oauth2callback = Blueprint('blueprint_google_oauth2callback', __name__)

@blueprint_google_oauth2callback.route('/oauth2callback')
def oauth2callback():
    # retrievesstate value from session to validate callback 
    state = session['state']
    
    # creates OAuth2 flow with client secrets file, authorization scopes, and state
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, AUTH_SCOPES, state=state)
    
    # set redirect URI for OAuth2 callback
    flow.redirect_uri = url_for('blueprint_google_oauth2callback.oauth2callback', _external=True)
    
    # get authorization response URL
    authorization_response = request.url

    try:
        # fetch token using authorization response and validates it
        token_response = flow.fetch_token(authorization_response=authorization_response)
        
        # gets credentials and stores them in session
        credentials = flow.credentials
        session['credentials'] = convert_credentials_to_dict(credentials)
        
        # saves Google Drive credentials to db for current user
        save_google_drive_credentials(current_user.get_id(), credentials)

        # sets google_drive_enabled to True for current user
        user = User.query.get(current_user.get_id())
        if user:
            user.google_drive_enabled = True
            db.session.commit()

        current_app.logger.info("Credentials retrieved successfully.")
        
        # checks if authenticated and sets flag
        if credentials and user:
            session['google_drive_connected'] = True

        # redirects to dashbord route 
        return redirect(url_for('main.dashboard'))

    except Exception as e:
        current_app.logger.error("Error! Can not get credentials:", exc_info=True)
        return jsonify(error="Error during fetching of credentials")


@blueprint_google_oauth2callback.route('/connect_google_drive')
def connect_google_drive():
    # creates OAuth2 flow using client secrets and authorization scopes
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=AUTH_SCOPES)

    # sets redirect URI to OAuth2 callback URL
    flow.redirect_uri = url_for('blueprint_google_oauth2callback.oauth2callback', _external=True)

    # generates authorization URL and state 
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    # stores state and marks Google Drive as connected in session
    session['state'] = state
    session['google_drive_connected'] = True

    # redirects  user to Google OAuth2 consent page
    return redirect(authorization_url)

# https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html
# https://googleapis.dev/python/google-auth-oauthlib/latest/reference/google_auth_oauthlib.flow.html
# https://stackoverflow.com/questions/71318804/google-oauth-2-0-failing-with-error-400-invalid-request-for-some-client-id-but
# https://ask.replit.com/t/bypassing-authentication-in-oauth-2-0-flask-app-in-python/52042/2
# https://github.com/googleapis/google-auth-library-python-oauthlib/blob/main/google_auth_oauthlib/flow.py
# https://googleapis.github.io/google-api-python-client/docs/oauth.html
# https://stackoverflow.com/questions/50865584/python-google-drive-api-oauth2-save-authorization-consent-for-user
# https://github.com/googleapis/google-api-php-client/blob/main/docs/oauth-web.md
# https://google-auth-oauthlib.readthedocs.io/en/latest/_modules/google_auth_oauthlib/flow.html
# https://googleapis.dev/python/google-auth-oauthlib/latest/_modules/google_auth_oauthlib/flow.html

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""