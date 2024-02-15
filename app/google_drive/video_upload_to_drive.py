import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

def store_video_to_google_drive(file_path, credentials, folder_id=None):
    try:
        # check if file exists at path
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            return None  # skips upload if file does not exist

        # creates Credentials object using credentials dictionary
        creds = Credentials(token=credentials['token'],
                            refresh_token=credentials['refresh_token'],
                            token_uri=credentials['token_uri'],
                            client_id=credentials['client_id'],
                            client_secret=credentials['client_secret'],
                            scopes=credentials['scopes'])
        
        # builds Google Drive service using the credentials
        service = build('drive', 'v3', credentials=creds)

        # defines metadata for uploaded file
        file_metadata = {'name': os.path.basename(file_path), 'mimeType': 'video/mp4'}
        
        # specifies folder 
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # create a MediaFileUpload object for uploading file
        media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
        
        # creates file in Google Drive and get its ID
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
         # return Google ID of uploaded file
        return file.get('id')

    except Exception as e:
        logging.error(f"Error in store_video_to_google_drive: {e}")
        raise


# References:
# https://developers.google.com/drive/api/quickstart/python
# https://developers.google.com/drive/api/guides/migrate-to-v3
# https://thepythoncode.com/code/using-google-drive--api-in-python
# https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html
# https://stackoverflow.com/questions/27771324/google-api-getting-credentials-from-refresh-token-with-oauth2client-client
# https://github.com/googleapis/google-auth-library-python/issues/659
# https://github.com/googleapis/google-auth-library-python/issues/501
# https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.http.MediaFileUpload-class.html
# https://googleapis.github.io/google-api-python-client/docs/media.html
# https://stackoverflow.com/questions/70020831/how-to-pass-file-to-google-drive-api-mediafileupload-without-saving-it-to-the
# https://developers.google.com/drive/api/guides/manage-uploads
# https://stackoverflow.com/questions/17658856/why-am-i-getting-a-filenotfounderror


""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """