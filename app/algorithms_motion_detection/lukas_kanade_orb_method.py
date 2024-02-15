import numpy as np
import cv2


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

class LukasKanadeOrb:
    #  initialize method with parameters
    def __init__(self, points_of_interest_detector, lucas_kanade_parameters, motion_detection_threshold):
        # detect points of interest using OpenCV
        # https://docs.opencv.org/4.x/db/d27/tutorial_py_table_of_contents_feature2d.html
        self.points_of_interest_detector = points_of_interest_detector
        # Lucas-Kanade optical flow parameters
        # https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html
        self.lucas_kanade_parameters = lucas_kanade_parameters
        # threshold for determining if motion is substantial
        self.motion_detection_threshold = motion_detection_threshold
        # contains previously detected points
        self.previous_points = None 

    # detects initial points of interest
    def detect_initial_keypoints(self, current_frame):
        # detected points
        detected_keypoints = self.points_of_interest_detector.detect(current_frame, None)
        # if keypoints are detected convert them to a numpy array
        self.previous_points = np.float32([kp.pt for kp in detected_keypoints]).reshape(-1, 1, 2) if detected_keypoints else None

    # tacks points from previous frame in grayscale to the current frame in grayscale
    def track_points_of_interest(self, previous_frame_gray, current_frame):
        if self.previous_points is not None:
            # calculates optical flow using the Lucas-Kanade method
            # https://docs.opencv.org/4.x/dc/d6b/group__video__track.html#ga473e4b884d6bcceedb5b30b2fb10ef0a
            new_points, status, error = cv2.calcOpticalFlowPyrLK(previous_frame_gray, current_frame, self.previous_points, None, **self.lucas_kanade_parameters)

            # checks for valid points tracking status
            good_new_points = new_points[status == 1]
            good_old_points = self.previous_points[status == 1]

            if good_new_points.size > 0 and good_old_points.size > 0:
                # checks that both arrays have the same shape
                minimum_length = min(len(good_new_points), len(good_old_points))
                good_new_points = good_new_points[:minimum_length]
                good_old_points = good_old_points[:minimum_length]

                # calculates points displacement between points (old and new)
                points_displacement = np.linalg.norm(good_new_points - good_old_points, axis=1)
                # if points are > motion detection threshold than it is a substantial motion
                substantial_motion = np.any(points_displacement > self.motion_detection_threshold)

                # updates previous points 
                self.previous_points = good_new_points.reshape(-1, 1, 2) if status.sum() > 0 else self.previous_points
            else:
                substantial_motion = False
                self.previous_points = None

            # returns substantial_motion (bool value) to indicate if motion is substantial
            # returns updated previous points for the next frame
            return substantial_motion, self.previous_points
        return False, self.previous_points

# References:
# https://docs.opencv.org/master/d4/dee/tutorial_optical_flow.html
# https://docs.opencv.org/3.4/db/d8e/tutorial_threshold.html
# https://docs.opencv.org/3.4/db/d27/tutorial_py_table_of_contents_feature2d.html
# https://pyimagesearch.com/2016/02/08/opencv-shape-detection/
# https://github.com/mbeyeler/opencv-python-blueprints/blob/master/chapter4/scene3D.py
# https://docs.opencv.org/3.4/dc/d6b/group__video__track.html
# https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
# http://jevois.org/tutorials/ProgrammerInvFlowLK.html
# https://answers.opencv.org/question/30130/best-method-for-multiple-particle-tracking-with-noise-and-possible-overlap/
# https://answers.opencv.org/question/82017/lucas-kanade-optical-flow-tracking-problem/
# https://stackoverflow.com/questions/22748024/opencv-grey-scale-conversion-error
# https://www.youtube.com/watch?v=dQrUilGMz_k
# https://learnopencv.com/optical-flow-in-opencv/
# https://medium.com/@VK_Venkatkumar/optical-flow-shi-tomasi-corner-detection-sparse-lucas-kanade-horn-schunck-dense-gunnar-e1dae9600df
# https://github.com/DragonComputer/Cerebrum/blob/master/cerebrum/vision/developmentExamples/opencv-optical-flow.py
# https://docs.opencv.org/4.x/d4/dee/tutorial_optical_flow.html
# https://medium.com/@guptachinmay321/an-insight-into-optical-flow-and-its-application-using-lucas-kanade-algorithm-c12f9f6e3773
# https://stackoverflow.com/questions/46176380/key-point-detection-and-image-stitching
# https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html
# https://numpy.org/devdocs/user/absolute_beginners.html
# https://gist.github.com/SammyVimes/b3af8bcf0ef6154568abd0a0513e46dc
# https://numpy.org/doc/stable/reference/arrays.scalars.html
# https://answers.opencv.org/question/73199/using-calcopticalflowpyrlk-with-multiple-user-defined-point/
# https://answers.opencv.org/question/25484/calcopticalflowpyrlk-losing-single-user-defined-tracking-point/
# https://docs.opencv.org/3.4/d2/d1d/samples_2cpp_2lkdemo_8cpp-example.html
# https://answers.opencv.org/question/115820/python-real-time-image-stabilization-with-optical-flow/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """