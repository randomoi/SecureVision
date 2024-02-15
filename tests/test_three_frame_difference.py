import unittest
from unittest.mock import patch
import numpy as np
import app.computer_vision.motion_analysis_utilities as mai  
import app.algorithms_motion_detection.three_frame_method as tfm  

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class TestThreeFrameDifferencing(unittest.TestCase):
    def test_three_frame_differencing_method(self):
        frame = np.random.randint(0, 255, (360, 640, 3), dtype=np.uint8)
        previous_frame_1 = np.random.randint(0, 255, (360, 640, 3), dtype=np.uint8)
        previous_frame_2 = np.random.randint(0, 255, (360, 640, 3), dtype=np.uint8)

        with patch('cv2.GaussianBlur', side_effect=lambda x, y, z: x), \
            patch('cv2.absdiff', side_effect=lambda x, y: np.abs(x - y)), \
            patch('cv2.bitwise_or', side_effect=lambda x, y: np.bitwise_or(x, y)), \
            patch('cv2.threshold', side_effect=lambda x, y, z, w: (None, x)), \
            patch('cv2.dilate', side_effect=lambda x, y, iterations: x):
                
            result = tfm.three_frame_differencing_method(frame, previous_frame_1, previous_frame_2)

            self.assertIsNotNone(result)
            self.assertEqual(result.shape, frame.shape)

class TestImageProcess(unittest.TestCase):
    def test_process_first_frame(self):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        resized_frame = np.random.randint(0, 255, (640, 360, 3), dtype=np.uint8)

        with patch('cv2.resize', return_value=resized_frame), \
            patch('cv2.cvtColor', side_effect=lambda x, y: x), \
            patch('cv2.GaussianBlur', side_effect=lambda x, y, z: x):

            frame_processed, gray = mai.process_initial_frame(frame)

            self.assertIsNotNone(frame_processed)
            self.assertIsNotNone(gray)
            self.assertEqual(frame_processed.shape, (640, 360, 3)) 

    def test_encode_frame_into_jpeg(self):
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        motion_data = {'test': 'data'}

        with patch('cv2.imencode', return_value=(True, np.array([1, 2, 3]))):
            jpeg, returned_motion_data = mai.convert_frame_to_jpeg(frame, motion_data)

            self.assertIsNotNone(jpeg)
            self.assertEqual(returned_motion_data, motion_data)


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