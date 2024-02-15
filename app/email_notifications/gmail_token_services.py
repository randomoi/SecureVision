from app.__init__ import db
from app.database_models.models import GmailToken
from datetime import datetime, timedelta, timezone

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# stores Gmail API tokens in db
def save_gmail_api_tokens_in_database(access_token, refresh_token, expires_in):
    # calculates token's expiration 
    expires_at = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=expires_in)
    # creates a new GmailToken with given values
    token = GmailToken(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        token_type="Bearer"  
    )
    # adds token object to db session
    db.session.add(token)
    # commits changes to db
    db.session.commit()

# updates Gmail API tokens in db
def update_gmail_api_tokens_in_database(access_token, expires_in, refresh_token=None):
     # calculates token's expiration 
    expires_at = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(seconds=expires_in)
    # checks if tokens exist in db
    tokens = GmailToken.get_tokens()
    # if yes, update existing tokens
    if tokens:
        tokens.access_token = access_token
        tokens.expires_at = expires_at
        if refresh_token:
            tokens.refresh_token = refresh_token
    else:
        # otherwise creates new token
        tokens = GmailToken(access_token=access_token, refresh_token=refresh_token, expires_at=expires_at, token_type="Bearer")
        
        # adds token object to db session
        db.session.add(tokens)
        
    # commits changes to db
    db.session.commit()

# References:
# https://stackoverflow.com/questions/51697374/gmail-api-error-when-access-token-expires-python-django-httpaccesstokenrefre
# https://community.auth0.com/t/oauth-token-not-returning-refresh-token/58093
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
# https://github.com/requests/requests-oauthlib/issues/324
# https://github.com/Colin-b/requests_auth/blob/develop/requests_auth/oauth2_tokens.py
# https://flask-oauthlib.readthedocs.io/en/latest/oauth2.html
# https://discuss.python.org/t/strange-inconsistency-in-datetime-timestamp-calculation/37214
# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""