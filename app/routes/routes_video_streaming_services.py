from app.camera.camera import VideoCamera
from app.database_models.models import User, MotionEvent
from flask_login import login_required,  current_user
from flask import session, Blueprint, current_app, Response, jsonify, request
from app.handlers.event_data_handler import save_motion_event_to_database
from app.google_drive.video_upload_to_drive import  store_video_to_google_drive
from app.google_drive.drive_token_manager import  retrieve_google_drive_credentials
from app.google_drive.drive_user_settings import check_if_user_has_enabled_google_drive
from app.google_drive.video_file_manager import retrieve_video_file_path
from app.google_drive.drive_utilities import retrieve_google_drive_video_url
import threading
import time
from app.email_notifications.email_notifications_all import send_email_with_preference_for_all_notifications
import atexit
import os
from app import db
import cv2
from app.algorithms_object_detection.object_detection_utilities import perform_image_processing_in_thread, object_recognition
from app.handlers.local_video_handler import save_video_in_local_directory
from config import BASE_DIRECTORY
from app.metadata.metadata_embedding import embed_metadata_on_video
from config import VIDEO_DIRECTORY
import logging


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')


blueprint_streaming_services = Blueprint('blueprint_streaming_services', __name__)

# initializes video camera outside of app context
video_camera = None

# constants 
SLEEP_DURATION = 1  
WAIT_TIMEOUT = 14  # timeout for waiting allows video to properly finalize
VIDEO_MIME_TYPE = 'multipart/x-mixed-replace; boundary=frame'
SLEEP_DURATION_TO_AVOID_BUSY = 0.1

# called when program is shut down to clean up resources
@atexit.register
def shutdown():
    global video_camera
    if video_camera:
        video_camera.__del__()

# serves video stream to users
@blueprint_streaming_services.route('/video_streamer')
@login_required  
def video_streamer():
    # creates HTTP response that calls video_live_stream; mimetype is streaming multipart content separated by a boundary marker 'frame'
    response = Response(video_live_stream(user_id=current_user.user_id, app=current_app._get_current_object()),
                        mimetype=VIDEO_MIME_TYPE)
    return response  # returns streaming response object


@blueprint_streaming_services.route('/enable_camera', methods=['POST'])
def enable_camera():
    global video_camera
    user_id = current_user.get_id()
    
    # verify if camera object is initialized, if not, initialize it
    if video_camera is None:
        creds = session.get('credentials')  # retrieves user credentials from session
        user_id = current_user.user_id  # retrieves current user's user_id
        
        # initializes a new VideoCamera instance
        video_camera = VideoCamera(app=current_app._get_current_object(), user_id=user_id, credentials=creds)

    # starts audio recording thread
    def sound_recording_thread():
        try:
            while True:
                # if camera is recording, read audio frames and add them to audio frames list
                if video_camera.is_video_recording:
                    sound_frame = video_camera.sound_stream.read(video_camera.chunk_size, exception_on_overflow=False)
                    video_camera.audio_frames.append(sound_frame)
                else:
                    time.sleep(SLEEP_DURATION_TO_AVOID_BUSY)  # otherwise sleep to avoid busy-waiting while not recording
        except Exception as e:
            logging.error("Error in audio recording thread: " + str(e))

    # starts audio recording thread
    sound_thread = threading.Thread(target=sound_recording_thread)
    sound_thread.start()

    try:
        video_camera._start_live_feed()

        # starts image analysis thread with updated arguments
        image_analysis_thread = threading.Thread(
            target=perform_image_processing_in_thread, 
            args=(
                video_camera, 
                video_camera.PATH_FOR_SAVING_IMAGE,
                video_camera.PATH_FOR_SAVING_PROCESSED_IMAGE,  
                video_camera.detection_model,  
                video_camera.category_index,   
                video_camera.DETECTION_THRESHOLD  
            )
        )
        image_analysis_thread.daemon = True
        image_analysis_thread.start()

        return jsonify(result="Camera is turned on.")
    except Exception as e:
        video_camera = None
        logging.error(f"Error starting camera live feed: {e}")
        return jsonify(error="Error starting camera live feed"), 500

@blueprint_streaming_services.route('/disable_camera', methods=['POST'])
def disable_camera():
    global video_camera
    # disable live feed if camera object exists
    if video_camera:
        video_camera._stop_live_feed()
        video_camera = None  # sets to None for proper re-initialization

    return jsonify(result="Camera is turned off.")


@blueprint_streaming_services.route('/setup_motion_detection_mode', methods=['POST'])
def setup_motion_detection_mode():
    global video_camera  
    motion_mode = request.form.get('mode')  # retrieves selected detection mode from form data
    
    user_id = current_user.get_id()  # retrieves current user's ID
    user = User.query.get(user_id)  # retrieves user from db using user_id
    
    if user:
        # updates user's mode in db
        user.motion_detection_mode = motion_mode
        db.session.commit()  # saves updated user information in db
        
        # if camera exists,  updates mode in camera instance
        if video_camera:  
            video_camera.setup_motion_detection_mode(motion_mode)
            
            return jsonify(result=f"Mode is set to {motion_mode}")  # responds with success message
        else:
            return jsonify(result="Camera instance is not available."), 500  # responds with error message
    else:
        return jsonify(result="User was not found."), 404  # responds with error if user is not found in db


# References:
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask
# https://docs.python.org/3/library/threading.html
# https://wiki.tcl-lang.org/page/multipart%2Fx-mixed-replace
# https://forum.opencv.org/t/about-using-webcamera-live-stream/11620
# https://github.com/psf/requests/issues/1554
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask/page/8
# https://github.com/miguelgrinberg/flask-video-streaming/issues/87
# https://stackoverflow.com/questions/44992241/video-stream-issue-with-multipart-x-mixed-replace-content-type
# https://stackoverflow.com/questions/41138443/multipartparser-end-stream-ended-unexpectedly
# https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
# https://stackoverflow.com/questions/62307644/python-flask-refresh-on-page-gives-problem-with-opencv-camera-object
# https://flask.palletsprojects.com/en/2.3.x/tutorial/views/
# https://stackoverflow.com/questions/63673551/pyaudio-audio-recording-python
# https://github.com/Motion-Project/motion/discussions/1366
# https://psychopy.org/api/hardware/camera.html
# https://forum.shotcut.org/t/audio-and-video-different-speed/42303
# https://forums.raspberrypi.com/viewtopic.php?t=173694
# https://gearspace.com/board/avid-pro-tools/1389498-frame-rate-audio-recording-pt.html
# https://groups.google.com/g/javacv/c/NCfGueArMM0
# https://stackoverflow.com/questions/64239939/how-to-synchronize-the-start-time-of-python-threads
# https://community.element14.com/products/raspberry-pi/f/forum/7235/play-and-record-audio-simultaneously-via-python-threading
# https://discourse.slicer.org/t/using-python-multithreading-in-3d-slicer/32299
# https://discuss.python.org/t/a-fast-free-threading-python/27903/86?page=5
# https://discuss.python.org/t/python-thread-only-running-at-launch-thread-interval/41405
# https://forum.image.sc/t/using-pyimagej-to-run-tensorflow-models-threading-issue/67783
# https://stackoverflow.com/questions/59371075/opencv-error-cant-open-camera-through-video-capture
# https://stackoverflow.com/questions/42018603/handling-get-and-post-in-same-flask-view
# https://flask-login.readthedocs.io/en/latest/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""
 
################################# MOVE TO ANOTHER FILE #################################

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

def video_live_stream(credentials=None, user_id=None, app=None):
    global video_camera  
    # if camera is not initialized, initializes it 
    if not video_camera:
        # creates VideoCamera instance
        video_camera = VideoCamera(app=app, user_id=user_id, credentials=credentials)
        # start new thread for handling database and email notifications 
        threading.Thread(target=monitor_and_handle_motion_events, args=(user_id, app)).start()

    while True:  # continuously streams video frames
        # check if video_camera object exists, if not displays message
        if not video_camera:
            time.sleep(SLEEP_DURATION)
            continue

        with app.app_context():  # use app context for thread safety
            # gets current frame from video camera
            frame, _ = video_camera.retrieve_frame()
            if frame:
                # if frame is available, yield it as part of response (multip-part format)
                yield (b'--frame\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                # if frame is unavailable, sleep 
                time.sleep(SLEEP_DURATION)


def monitor_and_handle_motion_events(user_id, app):
    global video_camera
    # continuously monitors and processes motion events
    while True:
        # if video_camera instance is None or missing  'events_motion_buffer' attribute.
        if video_camera is None or not hasattr(video_camera, 'events_motion_buffer'):
            time.sleep(SLEEP_DURATION) # pause before checking
            continue 

        # checks for motion events in buffer
        if video_camera.events_motion_buffer:
            # wait until video_ready_threading_event is set (allows to block thread until event is triggered)
            video_camera.video_ready_threading_event.wait()
 
            # processes each motion event in buffer
            while video_camera.events_motion_buffer:
                # pops 1st event from buffer and processes it 
                event = video_camera.events_motion_buffer.pop(0)
                process_motion_detection_event(event, user_id, app)

            # clears video_ready_threading_event to show that all events have been processed
            video_camera.video_ready_threading_event.clear()

        time.sleep(SLEEP_DURATION) # pauses loop to avoid running it


def process_motion_detection_event(event, user_id, app, wait_timeout=WAIT_TIMEOUT):
    # gets position, size, and image path 
    position_name = event['position_name']
    size_name = event['size_name']
    image_path = event['image_path']
    
    waiting_time = 0 # initializes waiting timer

    # this loop allows video camera to complete video recording, otherwise videos don't finalize properly resulting in unplayble videos
    while video_camera is not None and not video_camera.video_recording_complete and waiting_time < wait_timeout:
        time.sleep(SLEEP_DURATION)  # waits before checking again
        waiting_time += 1

    # checks if recording is finished after waiting loop
    if video_camera is not None and video_camera.video_recording_complete:
        # gets path to current video file
        current_video_path = video_camera.get_current_final_video_path()
 
        # if current video path is valid, object detection starts
        if current_video_path:
            detected_objects = process_object_detection(image_path, video_camera)
  
            # converts absolute path to relative path for video and image
            relative_path_for_video = os.path.relpath(current_video_path, BASE_DIRECTORY)
            relative_path_for_image = os.path.relpath(image_path, BASE_DIRECTORY)  


            with app.app_context():
                try:
                    # using app context saves event to db 
                    event_id = save_motion_event_to_database(
                        video_path=relative_path_for_video, 
                        image_path=relative_path_for_image, 
                        position_name=position_name,
                        size_name=size_name,
                        detected_objects=detected_objects, 
                        user_id=user_id
                    )

                    # if event was saved display success message; if not, display error message
                    if event_id is None:
                        logging.error("Did not save event to database.")
                    else:
                        logging.info(f"Event with ID: {event_id} was saved.")
                    
                    # Embed metadata into the video file.
                    metadata = {'position': position_name, 'size': size_name}
                    path_to_video_with_metadata = embed_metadata_on_video(current_video_path, metadata)
                    
                    # if metadata embedding was not successful, exit
                    if not path_to_video_with_metadata:
                        return  

                    # converts to relative path before updating db
                    relative_path_to_video_with_metadata = os.path.relpath(path_to_video_with_metadata, BASE_DIRECTORY)

                    # updates db with relative video path
                    event = MotionEvent.query.get(event_id)
                    if event:
                        event.video_path = relative_path_to_video_with_metadata
                        db.session.commit()

                    # manages video upload to google if activated otherwise saves video locally
                    manage_google_drive_video_upload(event_id, user_id, relative_path_to_video_with_metadata)
                    # sends email to user
                    send_email_notification(user_id, app, image_path)

                except Exception as e:
                    logging.error(f"Error! Can not process motion event: {e}", exc_info=True)


def send_email_notification(user_id, app, image_path):
    # gets user based on user_id
    user = User.query.get(user_id)
    
    # if user exists and email preference is set to 'all' 
    if user and user.email_notification_preference == 'all':
        # if token bucket allows sending notifications, sends email
        if video_camera.rate_limiting_token_bucket.consume():
            try:
                send_email_with_preference_for_all_notifications(app, user.email,"", image_path)
            except Exception as e:
                logging.error(f"Error! Can not send notification email: {e}")

def manage_google_drive_video_upload(event_id, user_id, current_video_path):
    # if user has Google Drive enabled, get their credentials
    if check_if_user_has_enabled_google_drive(user_id):
        credentials = retrieve_google_drive_credentials(user_id)

        if credentials:
            # gets local file path for event
            video_file_path = retrieve_video_file_path(event_id)

            if video_file_path:
                try:
                    # uploads video to Google Drive 
                    video_id = store_video_to_google_drive(video_file_path, credentials)
   
                    # retrieves Google Drive URL for uploaded video
                    google_drive_url = retrieve_google_drive_video_url(video_id)

                    # updates MotionEvent with Google Drive file ID
                    event = MotionEvent.query.get(event_id)
                    if event:
                        event.google_drive_file_id = video_id
                        event.video_path = google_drive_url  
                        db.session.commit()
                        logging.info(f"The event {event_id} was updated with Google Drive file ID {video_id}")

                    delay_seconds_before_deletion = 5
                    time.sleep(delay_seconds_before_deletion)

                    # if video uploaded to google drive, deletes local file
                    os.remove(video_file_path)
                except Exception as e:
                    logging.error(f"Error! Can not upload video to Google Drive: {e}")
        else:
            logging.error("Google Drive credentials were not found for user_id: {}".format(user_id))
    else:
        # if google drive is not enabled video is saved locally 
        local_path_for_video = save_video_in_local_directory(current_video_path)
        if local_path_for_video:
            logging.info(f"Video was saved at local path: {local_path_for_video}")


def process_object_detection(image_path, video_camera):
    # reads image from path
    frame = cv2.imread(image_path)
    _, detected_objects = object_recognition(
        frame,  # input image frame
        video_camera.detection_model, # trained detection model
        video_camera.category_index, # category index
        video_camera.DETECTION_THRESHOLD # threshold for detection of object
    )
    return detected_objects  # returns list of detected objects in image


# References: 
# https://learnopencv.com/reading-and-writing-videos-using-opencv/
# https://pyimagesearch.com/2021/01/20/opencv-load-image-cv2-imread/
# https://stackoverflow.com/questions/62307644/python-flask-refresh-on-page-gives-problem-with-opencv-camera-object
# https://stackoverflow.com/questions/57762334/image-streaming-with-opencv-and-flask-why-imencode-is-needed
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask/page/13
# https://github.com/miguelgrinberg/flask-video-streaming/blob/master/app.py
# https://stackoverflow.com/questions/15349997/assertionerror-when-threading-in-python
# https://discuss.python.org/t/struggling-with-threading-structure/36990
# https://medium.com/geekculture/an-introduction-to-threading-in-python-a5dc2af01ecd
# https://testdriven.io/blog/flask-contexts/
# https://stackoverflow.com/questions/77032578/working-with-threads-inside-flask-app-context
# https://stackoverflow.com/questions/6497113/sqlalchemy-query-issue
# https://github.com/sqlalchemy/sqlalchemy/issues/6055
# https://www.pythonanywhere.com/forums/topic/29540/
# https://docs.python.org/3/library/os.html
# https://www.w3schools.com/python/ref_os_remove.asp
# https://stackoverflow.com/questions/18954889/how-to-process-images-of-a-video-frame-by-frame-in-video-streaming-using-openc
# https://medium.com/@haydenfaulkner/extracting-frames-fast-from-a-video-using-opencv-and-python-73b9b7dc9661

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""