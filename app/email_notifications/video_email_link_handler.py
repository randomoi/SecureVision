from flask import url_for

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """


GOOGLE_DRIVE_FILE_BASE_URL = "https://drive.google.com/file/d/"
LOCAL_STATIC_PATH_DIR = 'app/static/'  
VIDEO_NOT_AVAILABLE_MESSAGE = "Video is not available." 
HTTPS_PROTOCOL = "https://"
GOOGLE_DRIVE_VIEW_PARAM = "/view?usp=drivesdk"


def retrieve_local_video_path(video_path):
    static_relative_path = video_path.replace(LOCAL_STATIC_PATH_DIR, '')
    return url_for('static', filename=static_relative_path, _external=True)

def retrieve_google_drive_file_id(file_id):
    return f"{GOOGLE_DRIVE_FILE_BASE_URL}{file_id}{GOOGLE_DRIVE_VIEW_PARAM}"

def no_video_available():
    return VIDEO_NOT_AVAILABLE_MESSAGE

def retrieve_video_link(event):
    if event.video_path and not event.video_path.startswith(HTTPS_PROTOCOL):
        return retrieve_local_video_path(event.video_path)
    elif event.google_drive_file_id:
        return retrieve_google_drive_file_id(event.google_drive_file_id)
    else:
        return no_video_available()
  
# References:  
# https://stackoverflow.com/questions/16351826/link-to-flask-static-files-with-url-for
# https://www.reddit.com/r/flask/comments/8wdjpy/url_for_question_can_it_be_used_for_things_other/

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """