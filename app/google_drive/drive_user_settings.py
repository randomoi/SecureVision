from app.database_models.models import User, GoogleDriveToken
from datetime import datetime
import logging


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

def check_if_user_has_enabled_google_drive(user_id):
   # query db  
    user = User.query.get(user_id)
    
    # checks if user exists and Google Drive is enabled 
    google_drive_enabled = user and user.google_drive_enabled
    
    # log result
    logging.info(f"Google Drive integration verification for user_id: {user_id}: {google_drive_enabled}")
    
    # return True if enabled, otherwise False
    return google_drive_enabled

def check_if_google_drive_enabled_and_connected(user_id):
    # logs
    logging.info(f"Google Drive integration and connection status for user_id: {user_id}")
    
    # checks if user enabled Google Drive
    user = User.query.get(user_id)
    if not user or not user.google_drive_enabled:
        logging.info("Google Drive is not enabled.")
        return False

    # check if Google Drive token is valid and not expired
    token = GoogleDriveToken.get_token_for_user(user_id)
    if token and datetime.utcnow() < token.expires_at:
        logging.info("Google Drive is connected.")
        return True
    else:
        logging.info("Google Drive is not connected.")
        return False


# https://stackoverflow.com/questions/6750017/how-to-query-database-by-id-using-sqlalchemy
# https://community.retool.com/t/authenticating-with-google-drive-so-that-all-users-can-access-the-files/14654
# https://community.auth0.com/t/google-drive-re-requesting-permission-every-time-a-user-logs-in/79957
# https://forums.insynchq.com/t/google-drive-your-authentication-token-is-invalid-please-try-logging-in-again/17430
# https://help.nextcloud.com/t/cant-add-local-folder-google-drive-to-nextcloud/123776
# https://stackoverflow.com/questions/77567553/google-drive-api-not-returning-subfolders-for-files-list-method-when-using-servi
# https://forum.duplicacy.com/t/google-drive-drive-appdata-scope-service-account-impersonate/4462

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""