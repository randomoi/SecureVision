from app.database_models.models import  GoogleDriveToken
from datetime import datetime, timedelta
from flask import current_app
from datetime import datetime, timedelta

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# saves google drive tokens
def save_google_drive_token(user_id, access_token, refresh_token, expires_in):
    # calculate texpiration for access token
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    # creates GoogleDriveToken object 
    token = GoogleDriveToken(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at
    )
    # saves token to db
    token.save_to_db()

# gets google drive creds
def retrieve_google_drive_credentials(user_id):
    # get Google Drive token for user
    token_entry = GoogleDriveToken.get_token_for_user(user_id)
    
    # verify if alid token exists and if token is not expired
    if token_entry and token_entry.expires_at > datetime.utcnow():
        return {
            'token': token_entry.access_token,
            'refresh_token': token_entry.refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token', 
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],  
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'], 
            'scopes': ['https://www.googleapis.com/auth/drive.file'] 
        }
    else:
        return None  

# References:
# https://developers.google.com/drive/api/guides/about-sdk
# https://developers.google.com/drive/api/guides/enable-sdk
# https://www.youtube.com/watch?v=1y0-IfRW114
# https://discuss.streamlit.io/t/google-drive-api-use-client-secret-file-json-within-secrets-file/56158
# https://forum.freecodecamp.org/t/google-drive-api-where-do-i-reference-credentials/343145
# https://stackoverflow.com/questions/39298451/google-api-invalid-request-after-access-token-expires
# https://developers.google.com/identity/protocols/oauth2
# https://forum.rclone.org/t/onedrive-and-googledrive-refreshing-tokens/37858
# https://github.com/googleapis/google-api-nodejs-client/issues/2350
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwjXydPC_paEAxUx0AIHHQmIBv8QFnoECDUQAQ&url=https%3A%2F%2Fwww.googlecloudcommunity.com%2Fgc%2FIntegration-Services%2Fexpired-access-token%2Fm-p%2F706141&usg=AOvVaw2e9jknfgxlJ2WkxIcyjC_b&opi=89978449
# https://www.truenas.com/community/threads/cloudsync-credentials-getting-google-drive-access-token-to-last-more-than-3600-seconds.71003/
# https://stackoverflow.com/questions/66816731/google-drive-api-with-python
# https://github.com/r-spatial/rgee/issues/139
# https://github.com/r-spatial/rgee/issues/139

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""
