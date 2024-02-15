from app.database_models.models import GmailToken
from app.email_notifications.gmail_token_services import update_gmail_api_tokens_in_database 
import requests
from datetime import datetime, timedelta, timezone
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, OAUTH2_TOKEN_URL, REFRESH_TOKEN_TYPE, TOKEN_EXPIRATION_BUFFER_IN_SECONDS

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

def retrieve_tokens_from_database():
    tokens = GmailToken.get_tokens() # get tokens from db
    if tokens:
        return tokens.access_token, tokens.refresh_token
    return None, None  # if tokens are not available, return (None, None)

# calculates expiration time
def calculate_expiration_time(expires_in):
    return datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=expires_in - TOKEN_EXPIRATION_BUFFER_IN_SECONDS)

# checks if token expired
def token_already_expired(token):
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)  
    expires_at = token.expires_at.replace(tzinfo=timezone.utc) if token.expires_at.tzinfo is None else token.expires_at
    return current_time > expires_at

#  obtains a new access token from the OAuth2 provider using the refresh token that was previously stored in the database.
def again_refresh_access_token():
    tokens = GmailToken.get_tokens()  # gets tokens from db
    if not tokens or not tokens.refresh_token:
        return None

    # prepares data for token refresh request
    data = {
        'grant_type': REFRESH_TOKEN_TYPE,
        'refresh_token': tokens.refresh_token,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET
    }

    try:
        response = requests.post(OAUTH2_TOKEN_URL, data=data)  # sends token refresh request
        response.raise_for_status()  # if request fails, raises an exception 
        response_data = response.json()  # parses response as JSON
    except requests.RequestException as e:
        print('Could not refresh access token:', e)
        return None

    # verifies if response contains new access token expiration time
    if 'access_token' in response_data and 'expires_in' in response_data:
        access_token = response_data['access_token']
        expires_in = response_data['expires_in']
        expires_at = calculate_expiration_time(expires_in)  # calculate expiration time
        update_gmail_api_tokens_in_database(access_token, expires_at, tokens.refresh_token)  # update tokens in db
        return access_token  # Return the refreshed access token
    else:
        print('Could not refresh access token:', response_data)
        return None 

 
#  checks if an access token exists and has expired; a refresh token is used to revalidate an expired token.
#  if the refresh works, it returns the updated access token; None if no valid token is available.   
def retrieve_access_token():
    # checks if token expired
    tokens = GmailToken.get_tokens()  # gets tokens from db
    if token_already_expired(tokens):  # checks if token expired
        return again_refresh_access_token()  # tries to refresh access token
    return tokens.access_token if tokens else None

# References:
# https://developers.google.com/identity/protocols/oauth2
# https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow
# https://cloud.google.com/apigee/docs/api-platform/security/oauth/access-tokens
# https://medium.com/automationmaster/getting-google-oauth-access-token-using-google-apis-18b2ba11a11a
# https://support.google.com/cloud/answer/6158849?hl=en
# https://cloud.google.com/docs/authentication/token-types
# https://www.oauth.com/oauth2-servers/signing-in-with-google/
# https://medium.com/@tony.infisical/guide-to-using-oauth-2-0-to-access-google-apis-dead94d6866d
# https://www.youtube.com/watch?v=NIlK6gAwKEM
# https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens.html
# https://github.com/nextauthjs/next-auth/issues/8034
# https://community.auth0.com/t/accesstokenerror-when-access-token-is-not-expired/122729
# https://www.oauth.com/oauth2-servers/making-authenticated-requests/refreshing-an-access-token/
# https://forum.osticket.com/d/101504-token-expired
# https://community.auth0.com/t/oauth-token-not-returning-refresh-token/58093
# https://github.com/nextauthjs/next-auth/discussions/3940
# https://stackoverflow.com/questions/50242996/current-method-to-get-new-access-token-from-refresh-token
# https://github.com/nextauthjs/next-auth/issues/2071
# https://developer-community.sage.com/topic/210-refresh-token-is-invalid-for-oauth20/
# https://community.auth0.com/t/refresh-token-grant-type-does-not-return-a-new-refresh-token/13510
# https://stackoverflow.com/questions/55486341/how-to-secure-a-refresh-token

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""