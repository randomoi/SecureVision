from app.__init__ import db
from app.database_models.models import GoogleDriveToken
from datetime import datetime, timedelta

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# saves GDrive credentails
def save_google_drive_credentials(user_id, credentials):
    # convert credentials to a dictionary
    creds_dict = convert_credentials_to_dict(credentials)
    # calculates expiration in secs
    expires_in = (credentials.expiry - datetime.utcnow()).total_seconds()  

    # saves tokens to db
    google_drive_token = GoogleDriveToken.query.filter_by(user_id=user_id).first()
    if google_drive_token:
        google_drive_token.access_token = creds_dict['token']
        google_drive_token.refresh_token = creds_dict['refresh_token']  
        google_drive_token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    else:
        # creates a new Googel Drive token
        new_token = GoogleDriveToken(
            user_id=user_id,
            access_token=creds_dict['token'],
            refresh_token=creds_dict['refresh_token'],
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        db.session.add(new_token) # adds to session
    db.session.commit() # commits tokens to db

# converts credentials to dictionary
def convert_credentials_to_dict(credentials):
    return {'token': credentials.token, 
            'refresh_token': credentials.refresh_token, 
            'token_uri': credentials.token_uri, 
            'client_id': credentials.client_id, 
            'client_secret': credentials.client_secret, 
            'scopes': credentials.scopes}


# References:
# https://developers.google.com/identity/protocols/oauth2/web-server
# https://googleapis.dev/python/google-auth/1.12.0/_modules/google/oauth2/credentials.html
# https://community.auth0.com/t/get-refresh-token-when-requesting-client-credentials/111184
# https://github.com/googleapis/google-api-python-client/issues/807
# https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html
# https://stackoverflow.com/questions/72827460/creating-google-credentials-object-for-google-drive-api-without-loading-from-fil
# https://discuss.dvc.org/t/error-configuration-error-gdrive-remote-auth-failed-with-credentials-in-gdrive-credentials-data/1254
# https://discuss.dvc.org/t/gdrive-user-credentials-json-is-missing/1453
# https://github.com/googleapis/google-auth-library-python/issues/659
# https://stackoverflow.com/questions/51883184/google-oauth2-not-issuing-a-refresh-token-even-with-access-type-offline
# https://groups.google.com/g/google-doubleclick-for-advertisers-api/c/9BRYDoT7RH0/m/tIfJUVwjAQAJ
# https://stackoverflow.com/questions/45501082/set-google-application-credentials-in-python-project-to-use-google-api

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""