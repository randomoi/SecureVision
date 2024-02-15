import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from app.algorithms_motion_detection.lukas_kanade_orb_method import LukasKanadeOrb 

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class TestLukasKanadeOrb(unittest.TestCase):
# initializes mocks and test data 
    def setUp(self):
        self.points_of_interest_detector = MagicMock()
        self.lucas_kanade_parameters = {'winSize': (10, 10), 'maxLevel': 2, 'criteria': (3, 14, 0.02)}
        self.motion_detection_threshold = 1.0
        self.lucas_kanade_orb = LukasKanadeOrb(self.points_of_interest_detector, self.lucas_kanade_parameters, self.motion_detection_threshold)
        
    @patch('cv2.KeyPoint')
    def test_initial_keypoints(self, mock_keypoint):
        mock_keypoint.pt = [150, 250]
        self.points_of_interest_detector.detect.return_value = [mock_keypoint]

        current_frame = np.zeros((480, 640), dtype=np.uint8)  
        self.lucas_kanade_orb.detect_initial_keypoints(current_frame)

        self.assertIsNotNone(self.lucas_kanade_orb.previous_points)  # checks previous_points is not None
        self.assertEqual(self.lucas_kanade_orb.previous_points[0][0][0], 150)  # checks x coord of tracked point
        self.assertEqual(self.lucas_kanade_orb.previous_points[0][0][1], 250)  # Check y coord of tracked point

    @patch('cv2.calcOpticalFlowPyrLK')
    def test_track_points_of_interest(self, mock_calc_optical_flow):
        new_points = np.array([[[115, 215]]], dtype=np.float32)
        status = np.array([[1]], dtype=np.uint8)
        error = np.array([[0.01]], dtype=np.float32)
        mock_calc_optical_flow.return_value = (new_points, status, error)

        self.lucas_kanade_orb.previous_points = np.array([[[160, 270]]], dtype=np.float32)

        previous_frame_gray = np.zeros((360, 640), dtype=np.uint8)
        current_frame = np.zeros((360, 640), dtype=np.uint8)

        substantial_motion, _ = self.lucas_kanade_orb.track_points_of_interest(previous_frame_gray, current_frame)

        self.assertTrue(substantial_motion)  


if __name__ == '__main__':
    unittest.main()
    
# References:
# https://docs.python.org/3/library/unittest.mock.html
# https://docs.python.org/3/library/unittest.mock-examples.html
# https://www.toptal.com/python/an-introduction-to-mocking-in-python
# https://datageeks.medium.com/python-unittest-a-guide-to-patching-mocking-and-magicmocks-40f2c0738981
# https://flask.palletsprojects.com/en/2.3.x/testing/
# https://pytest-flask.readthedocs.io/en/latest/
# https://circleci.com/blog/testing-flask-framework-with-pytest/
# https://pypi.org/project/pytest-flask/
# https://stackoverflow.com/questions/12187122/assert-a-function-method-was-not-called-using-mock
# https://realpython.com/python-mock-library/
# https://flask-restless.readthedocs.io/en/0.9.2/customizing.html
# https://stackoverflow.com/questions/29834693/unit-test-behavior-with-patch-flask
# https://stanford-code-the-change-guides.readthedocs.io/en/latest/guide_flask_unit_testing.html
# https://stackoverflow.com/questions/20242862/why-python-mock-patch-doesnt-work
# https://github.com/pydantic/pydantic/discussions/7741
# https://www.fugue.co/blog/2016-02-11-python-mocking-101
# https://fgimian.github.io/blog/2014/04/10/using-the-python-mock-library-to-fake-regular-functions-during-tests/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""