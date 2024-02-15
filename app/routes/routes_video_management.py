from app.database_models.models import MotionEvent, GoogleDriveToken, DetectedObject
from flask import session, current_app, jsonify, request, Blueprint, url_for
from flask_login import login_required, current_user
from app import db
import datetime
from datetime import datetime
from sqlalchemy import func
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.database_models.models import GoogleDriveToken
from app.google_drive.drive_user_settings import check_if_google_drive_enabled_and_connected
from app.google_drive.drive_token_manager import  retrieve_google_drive_credentials
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, AUTH_SCOPES
import os
from flask import session, Blueprint, current_app, jsonify, request
import logging

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

logging.basicConfig(level=logging.DEBUG)

blueprint_video_management = Blueprint('blueprint_video_management', __name__)

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%I:%M %p'
GOOGLE_DRIVE_TOKEN_URI = 'https://oauth2.googleapis.com/token'
WEBVIEWLINK = 'webViewLink'
FFIELDS_DOWNLOAD_LINK = 'https://drive.google.com/uc?export=download&id='
ERROR_FILEID = "File ID received for deletion is unknown."
DELETE_ERROR = "Error deleting video file."
SUCCESS_DELETE_MESSAGE = "Video deleted successfully."
ERROR_INVALID_CREDS = "Invalid/expired credentials."
GOOGLE_DRIVE_SERVICE_NAME = 'drive'
GOOGLE_DRIVE_SERVICE_VER = 'v3'

@blueprint_video_management.route('/retrieve-google-videos-for-date')
@login_required
def retrieve_google_videos_for_date():
    # gets selected date from request (default current date)
    selected_date_string = request.args.get('date', datetime.today().strftime(DATE_FORMAT))
    date_selected = datetime.strptime(selected_date_string, DATE_FORMAT).date()

    # queries sb for camera events matching selected date and current user
    events = MotionEvent.query.filter(
        func.date(MotionEvent.timestamp) == date_selected,
        MotionEvent.user_id == current_user.user_id
    ).all()

    # initializes a list to store video data 
    data_for_video = []

    # gets Google Drive token for current user
    google_drive_token = GoogleDriveToken.get_token_for_user(current_user.user_id)

    # checks if valid Google Drive token exists
    if google_drive_token and google_drive_token.expires_at > datetime.utcnow():
        # create credentials dictfor Google Drive API
        credentials_dict = {
            'token': google_drive_token.access_token,
            'refresh_token': google_drive_token.refresh_token,
            'token_uri': GOOGLE_DRIVE_TOKEN_URI,
            'client_id': GOOGLE_CLIENT_ID,  
            'client_secret': GOOGLE_CLIENT_SECRET,  
            'scopes': [AUTH_SCOPES]
        }
        creds = Credentials(**credentials_dict)
        service = build(GOOGLE_DRIVE_SERVICE_NAME, GOOGLE_DRIVE_SERVICE_VER, credentials=creds)

        # loops over camera events and processes Google Drive links
        for event in events:
            if event.google_drive_file_id:  # checks if Google Drive ID is available
                try:
                    # gets  webViewLink of Google Drive file
                    file = service.files().get(fileId=event.google_drive_file_id, fields='webViewLink').execute()
                    video_link = file.get(WEBVIEWLINK)
                    download_link = FFIELDS_DOWNLOAD_LINK + event.google_drive_file_id

                    # fetchs detected objects for each event
                    detected_objects = DetectedObject.query.filter_by(motion_event_id=event.event_id).all()
                    detected_objects_details = ', '.join([obj.class_name for obj in detected_objects])

                    # gets position and intruder size 
                    position_details = event.position.name if event.position else 'Unknown'
                    intruder_size_details = event.motion_size.size_name if event.motion_size else 'Unknown'

                    # adds video data to list
                    data_for_video.append({
                        'google_drive_file_id': event.google_drive_file_id,
                        'source': 'google_drive',
                        'link': video_link,
                        'downloadLink': download_link,
                        'capture_time': event.timestamp.strftime(TIME_FORMAT),
                        'detected_objects': detected_objects_details,
                        'position': position_details,
                        'motion_size': intruder_size_details
                    })
                except Exception as e:
                    logging.error(f"Error! Can not access Google Drive for event ID {event.event_id}: {e}")
            else:
                logging.debug(f"Event ID {event.event_id} does not have Google Drive file id.")
    else:
        logging.info("Skipping Google Drive video fetch. Google Drive token was not found. ")

    # returns video data as JSON response
    return jsonify(data_for_video)

@blueprint_video_management.route('/retrieve-local-videos-for-date', methods=['GET'])
@login_required
def retrieve_local_videos_for_date():
    selected_date_string = request.args.get('date', datetime.today().strftime(DATE_FORMAT))
    date_selected = datetime.strptime(selected_date_string, DATE_FORMAT).date()

    events = MotionEvent.query.filter(
        func.date(MotionEvent.timestamp) == date_selected,
        MotionEvent.user_id == current_user.user_id
    ).all()

    data_for_video = []

    for event in events:
        if event.video_path and not event.video_path.startswith("http"):
            static_relative_path = event.video_path.replace('app/static/', '')
            capture_time = event.timestamp.strftime(TIME_FORMAT)

            # gets detected objects for each event
            detected_objects = DetectedObject.query.filter_by(motion_event_id=event.event_id).all()
            detected_objects_details = ', '.join([obj.class_name for obj in detected_objects])

            # gets position and intruder size 
            position_details = event.position.name if event.position else 'Unknown'
            intruder_size_details = event.motion_size.size_name if event.motion_size else 'Unknown'

            data_for_video.append({
                'source': 'local',
                'link': url_for('static', filename=static_relative_path),
                'capture_time': capture_time,
                'detected_objects': detected_objects_details,
                'position': position_details,
                'motion_size': intruder_size_details,
            })

    return jsonify(data_for_video)
   
@blueprint_video_management.route('/delete-local-video/<string:video_file_name>', methods=['DELETE'])
@login_required
def delete_local_video(video_file_name):
    try:
        # gets MotionEvent object by video file name
        event = MotionEvent.query.filter_by(video_path=f'app/static/videos/{video_file_name}').first()

        # checks if event belongs to current user
        if event and event.user_id == current_user.user_id:
            # gets local video file path
            local_path_for_video = event.video_path

            # checks if video file path exists
            if local_path_for_video and os.path.exists(local_path_for_video):
                # deletes local video file
                os.remove(local_path_for_video)

                # delete event from db
                db.session.delete(event)
                db.session.commit()

                return jsonify({'success': 'Local video file was deleted.'})
            else:
                return jsonify({'error': 'Local video file was not found.'}), 404
        else:
            return jsonify({'error': 'Unauthorized'}), 401

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@blueprint_video_management.route('/get-available-dates')
@login_required
def get_available_dates():
    # query db to get all unique dates for video events for the current user
    dates_query = MotionEvent.query.with_entities(
        func.date(MotionEvent.timestamp).label('unique_date')
    ).filter_by(
        user_id=current_user.user_id
    ).distinct().order_by(MotionEvent.timestamp.desc())

    # formats dates JSON serialization
    unique_dates = [datetime.strptime(date, DATE_FORMAT).strftime(DATE_FORMAT) for date, in dates_query]

    # returns unique dates as JSON response
    return jsonify(unique_dates=unique_dates)

@blueprint_video_management.route('/delete-google-drive-video/<fileId>', methods=['DELETE'])
@login_required
def delete_google_drive_video(fileId):
    # checks if file Id is undefined
    if fileId == 'undefined':
        current_app.logger.error("Undefined file ID received for deletion.")
        return jsonify({"error": ERROR_FILEID}), 400  # bad request

    # gets user ID of current user
    user_id = current_user.get_id()

    # gets Google Drive credentials for user
    credentials = retrieve_google_drive_credentials(user_id)

    # deletes video from Google Drive
    if credentials:
        creds = Credentials(**credentials)
        service = build(GOOGLE_DRIVE_SERVICE_NAME, GOOGLE_DRIVE_SERVICE_VER, credentials=creds)
        try:
            service.files().delete(fileId=fileId).execute()
            current_app.logger.info(f"Google Drive video with ID {fileId} was deleted.")

            # deletes video record from db
            event_to_delete = MotionEvent.query.filter_by(google_drive_file_id=fileId).first()
            if event_to_delete:
                db.session.delete(event_to_delete)
                db.session.commit()
                current_app.logger.info(f"Deleted event with Google Drive ID {fileId} from db.")
            else:
                current_app.logger.warning(f"No event was found with Google Drive ID {fileId} in db.")

        except Exception as e:
            current_app.logger.error(f"Error! Can not delete Google Drive video: {e}", exc_info=True)
            return jsonify({"error": DELETE_ERROR}), 500
    else:
        current_app.logger.warning("Invalid or expired Google Drive credentials.")
        return jsonify({"error": ERROR_INVALID_CREDS}), 401

    # return success response
    return jsonify({"success": SUCCESS_DELETE_MESSAGE}), 200

@blueprint_video_management.route('/check-google-drive-connection')
@login_required
def check_google_drive_connection():
    # retrieves flag from session
    connected_one_time = session.pop('google_drive_connected', False)
    
    # returns a JSON response indicating if Google Drive was connected 
    return jsonify({'connectedOneTime': connected_one_time})

@blueprint_video_management.route('/api/google-drive/status')
@login_required
def status_of_google_drive():
    # get user ID of current user
    user_id = current_user.get_id()
    
    # checks if Google Drive is enabled and connected for user
    is_connected = check_if_google_drive_enabled_and_connected(user_id)
    
    # return JSON response 
    return jsonify({'isConnected': is_connected})

# References:
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
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html
# https://stackoverflow.com/questions/53460391/passing-a-date-as-a-url-parameter-to-a-flask-route
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
# https://developers.google.com/drive/api/guides/manage-downloads
# https://developers.google.com/drive/api/guides/manage-changes
# https://developers.google.com/drive/api/reference/rest/v3/files
# https://issuetracker.google.com/issues/149154237?pli=1
# https://gist.github.com/iamtekeste/3cdfd0366ebfd2c0d805?permalink_comment_id=3446796
# https://www.programiz.com/python-programming/methods/list/append
# https://www.fullstackpython.com/flask-json-jsonify-examples.html
# https://stackoverflow.com/questions/39480914/why-db-session-remove-must-be-called
# https://developers.google.com/drive/api/reference/rest/v2/files/delete
# https://stackoverflow.com/questions/15118145/delete-a-file-using-google-drive-api
# https://moodle.org/mod/forum/discuss.php?d=233030
# https://stackoverflow.com/questions/53094104/get-the-user-id-in-flask
# https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """