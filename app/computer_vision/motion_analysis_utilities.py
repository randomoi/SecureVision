from config import VIDEO_DIRECTORY
import logging
from app.database_models.models import User
from enum import Enum
import cv2
import logging


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """


# configures logging
# https://docs.python.org/3/library/logging.html
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

# constance declaration
THRESHOLD_PERCENTAGE = 0.05
DIVISOR = 2  # divisor
BOUNDARY_FACTOR_FOR_CENTER_RIGHT = 2  # boundary between "Center" and "Right" positions

RESIZE_FRAME_DIMENSIONS = (640, 360)  # used to resize frames dimensions
KERNEL_SIZE_GRAYSCALE_BLUR = (21, 21)  # used for blurring in grayscale 
STD_DEV_GAUSSIAN_BLUR = 0 # standard deviation for gaussian blur (set to 0 -> calculated from the kernel size)
JPEG_FORMAT = '.jpg'

# provides set of pre-defined options
class MotionSizeName(Enum):
    SMALL = "Small"
    LARGE = "Large"

# provides set of pre-defined options
class MotionPositionName(Enum):
    LEFT = "Left"
    RIGHT = "Right"

# processes motion data and buffers it for later
def process_and_buffer_motion_data(events_motion_buffer, motion_data, user_id, app):
    # identifies position and size
    position_name = identify_position(motion_data["x"], motion_data["w"], motion_data["frame_width"])
    size_name = identify_size(motion_data["contour_area"], motion_data["frame_width"], motion_data["frame_height"])
    event_data = {
        'video_path': VIDEO_DIRECTORY, 
        'image_path': motion_data["image_path"], 
        'position_name': position_name,
        'size_name': size_name,
        'user_id': user_id
    }
    events_motion_buffer.append(event_data)
    logging.debug(f"Motion data buffered: {event_data}")

# identifies position of motion
def identify_position(x, w, frame_width):
    # splits frame 
    x_center = x + w / DIVISOR
    
    # calculates midpoint of frame
    midpoint_of_frame = frame_width / 2

    # determins if motion is on left or right based on center point
    if x_center < midpoint_of_frame:
        return MotionPositionName.LEFT.value
    else:
        return MotionPositionName.RIGHT.value # returns string postion

# identifies size of motion/intruder based on area (area is a float)
def identify_size(contour_area, frame_width, frame_height):
    # calculates total  area of frame 
    total_area_of_frame = frame_width * frame_height
    
    # calculates % of frame that contour occupies
    percentage_of_area = (contour_area / total_area_of_frame) * 100
    
    # determines size category 
    if percentage_of_area < THRESHOLD_PERCENTAGE:
        return MotionSizeName.SMALL.value
    else:
        return MotionSizeName.LARGE.value

# gets user's set motion detection mode from db, if user did not select mode default will be used
def get_detection_mode_for_user(app, user_id, default_mode='mgo2'):
    # uses app context to access db and get user settings
    # https://docs.sqlalchemy.org/en/14/orm/query.html
    with app.app_context():
        user = User.query.get(user_id)
        if user and user.motion_detection_mode:
            logging.info(f"Retrieved detection mode for user {user_id}: {user.motion_detection_mode}")
            return user.motion_detection_mode
        else:
            logging.warning(f"User {user_id} did not set detection mode using default 'mgo2'")
            return 'mgo2' # returns string user's detection mode


# resizes, converts to grayscale and applies gausian blur for first frame
def process_initial_frame(frame):
    # https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
    frame = cv2.resize(frame, RESIZE_FRAME_DIMENSIONS)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, KERNEL_SIZE_GRAYSCALE_BLUR, STD_DEV_GAUSSIAN_BLUR)
    return frame, gray_frame

# converts frame to jped
def convert_frame_to_jpeg(frame, motion_data):
    jpeg = None

    # verify if frame is valid 
    if frame is not None:
        try:
            # encodes frame to jpeg, cv2.imencode returns a tuple (success flag, converted image)
            # https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html
            ret, jpeg = cv2.imencode(JPEG_FORMAT, frame)

            # verify if conversion was successful
            if ret:
                # converts to bytes and returns with motion_data
                return jpeg.tobytes(), motion_data
            else:
                logging.error("Frame conversion failed.")
                return None, None
        except Exception as e:
            logging.error(f"Error! Exception during frame conversion: {e}")
            return None, None
    else:
        logging.error("Error! Frame is None, cannot convert to jpeg.")
        return None, None

# References:
# https://docs.python.org/3/library/enum.html
# https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html
# https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html
# https://docs.python.org/3/library/logging.html
# https://stackoverflow.com/questions/34122949/working-outside-of-application-context-flask
# https://flask.palletsprojects.com/en/2.3.x/appcontext/
# https://stackoverflow.com/questions/76137018/problem-while-trying-to-save-a-frame-after-every-1-second-using-opencv
# https://docs.opencv.org/3.4/df/d9d/tutorial_py_colorspaces.html
# https://pyimagesearch.com/2021/01/20/opencv-resize-image-cv2-resize/
# https://www.tutorialkart.com/opencv/python/opencv-python-resize-image/#gsc.tab=0
# https://docs.opencv.org/3.4/d4/d13/tutorial_py_filtering.html
# https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/
# https://docs.opencv.org/3.4/d4/d86/group__imgproc__filter.html
# https://www.geeksforgeeks.org/python-opencv-cv2-cvtcolor-method/
# https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html
# https://github.com/tiangolo/fastapi/issues/2956
# https://answers.opencv.org/question/202145/how-to-decode-by-imdecode/
# https://www.opencv.org.cn/opencvdoc/2.3.2/html/modules/highgui/doc/reading_and_writing_images_and_video.html

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """
