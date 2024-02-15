import cv2
import numpy as np
from app.algorithms_motion_detection.three_frame_method import three_frame_differencing_method
import logging
import time

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """


# configures logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

# constant for #of dimensions for grayscale image
NUMBER_OF_GRAYSCALE_DIMENSIONS = 2

class ModeProcessor:

    MEDIAN_BLUR_VALUE = 5 
    def __init__(self, mgo2_background_subtractor, lucas_kanade_orb_detection_tracking, mckenna_background_subtractor, detection_model, category_index, detection_threshold):
        self.mgo2_background_subtractor = mgo2_background_subtractor
        self.lucas_kanade_orb_detection_tracking = lucas_kanade_orb_detection_tracking
        self.mckenna_background_subtractor = mckenna_background_subtractor
        self.detection_model = detection_model
        self.category_index = category_index
        self.detection_threshold = detection_threshold

    # processes mgo2 background subtractor and three frame diffencing 
    def process_mgo2_and_three_frame_diff_mode(self, gray_frame, previous_frame_1, previous_frame_2, callback_for_detect_motion, frame):
        try:
            # checks if previous frames have been initialized for three-frame differencing
            if previous_frame_1 is None or previous_frame_2 is None:
                return None

            # applies background subtraction using mgo2_background_subtractor
            foreground_mask_mgo2 = self.mgo2_background_subtractor.apply(gray_frame)

            # creates mask using three-frame differencing method to detect motion
            three_frame_differencing_mask = three_frame_differencing_method(gray_frame, previous_frame_1, previous_frame_2)

            # combines foreground_mask_mgo2 and three_frame_differencing_mask using bitwise AND (only areas detected by both methods will be considered)
            motion_mask = cv2.bitwise_and(three_frame_differencing_mask, foreground_mask_mgo2)

            # applies a median blur to motion mask to reduce noise 
            motion_mask = cv2.medianBlur(motion_mask, self.MEDIAN_BLUR_VALUE)

            # detect motion using the designated method and return motion data
            motion_data = callback_for_detect_motion(motion_mask, frame)
            
            return motion_data  
        
        except Exception as e:
            logging.error(f"Error in process_mgo2_and_three_frame_diff_mode: {str(e)}")
            raise e

    # processes barnish and three frame differencing        
    def process_lucas_kanade_orb_and_three_frame__diff_mode(self, gray_frame, frame, previous_frame, previous_frame_1, previous_frame_2, callback_for_detect_motion, video_camera_start_time, warm_up_period):
        try:
            current_time = time.time()
            if current_time - video_camera_start_time < warm_up_period:
                return False  # skip detection during warmup

            # initialize lucas_kanade_orb method 
            if self.lucas_kanade_orb_detection_tracking.previous_points is None:
                self.lucas_kanade_orb_detection_tracking.detect_initial_keypoints(gray_frame)

            # continue tracking points of interest vetween previous and current frame for motion detection
            motion_detected_by_lucas_kanade_orb, _ = self.lucas_kanade_orb_detection_tracking.track_points_of_interest(previous_frame, gray_frame)

            # applies three frame dff for motion detection
            motion_mask = three_frame_differencing_method(gray_frame, previous_frame_1, previous_frame_2)
            # uses callback func to analyse mask
            motion_detected_by_three_frame_diff = callback_for_detect_motion(motion_mask, frame)
            
            # decides if substantial motion was detected by either method
            motion_data = motion_detected_by_lucas_kanade_orb or motion_detected_by_three_frame_diff
            
            return motion_data 

        except Exception as e:
            logging.error(f"Error in process_lucas_kanade_orb_and_three_frame__diff_mode: {str(e)}")
            raise e


    # processes mckenna and three frame differencing     
    def process_mckenna_and_three_frame_diff_mode(self, gray_frame, frame, previous_frame_1, previous_frame_2, callback_for_detect_motion):
        try:
            # initialize processing with McKenna method
            mckenna_foreground_mask = self.mckenna_background_subtractor.process_one_frame(frame)

            # create mask using three-frame differencing to detect motion
            three_frame_differencing_mask = three_frame_differencing_method(gray_frame, previous_frame_1, previous_frame_2)

            # resize masks 
            if three_frame_differencing_mask.shape != mckenna_foreground_mask.shape:
                three_frame_differencing_mask = cv2.resize(three_frame_differencing_mask, (mckenna_foreground_mask.shape[1], mckenna_foreground_mask.shape[0]))

            # convert masks to data types
            mckenna_foreground_mask = mckenna_foreground_mask.astype(np.uint8)
            three_frame_differencing_mask = three_frame_differencing_mask.astype(np.uint8)
            
            # verify if three-frame difference mask is in grayscale 
            if three_frame_differencing_mask.ndim == NUMBER_OF_GRAYSCALE_DIMENSIONS:
                # convertz grayscale mask to BGR format 
                three_frame_differencing_mask = cv2.cvtColor(three_frame_differencing_mask, cv2.COLOR_GRAY2BGR)

            # uses bitwais OR to create motion mask
            motion_mask = cv2.bitwise_or(mckenna_foreground_mask, three_frame_differencing_mask)

            # callback_for_detect_motion to detect motion and return the motion data
            motion_data = callback_for_detect_motion(motion_mask, frame)
 
            return motion_data

        except Exception as e:
            logging.error(f"Error in process_mckenna_and_three_frame_diff_mode: {str(e)}")
            raise e

# References:
# https://docs.opencv.org/4.x/db/d5c/tutorial_py_bg_subtraction.html
# https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html
# http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.675.203&rep=rep1&type=pdf
# https://learnopencv.com/faster-r-cnn-object-detection-with-pytorch/
# https://stackoverflow.com/questions/22196062/frame-difference-methodbackground-subtraction
# https://www.reddit.com/r/learnpython/comments/10mzu2s/very_basic_motion_detection_through_opencv_frame/
# https://answers.opencv.org/question/181877/frame-difference-based-tracker-stuck-with-first-frame/
# https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2
# https://stackoverflow.com/questions/71737841/opencv-c-sharp-frame-differencing
# https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2
# https://www.youtube.com/watch?v=GeqSF8EV1Gs
# https://stackoverflow.com/questions/71737841/opencv-c-sharp-frame-differencing
# https://www.researchgate.net/publication/376076200_Motion_Detection_Using_Three_Frame_Differencing_and_CNN
# https://stackoverflow.com/questions/66876520/how-to-extract-foreground-form-a-moving-camera-by-using-opencv

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

