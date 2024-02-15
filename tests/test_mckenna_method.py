import unittest
from unittest.mock import patch
import numpy as np
from app.algorithms_motion_detection.mckenna_method import McKennaMethod  

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class TestMcKennaMethod(unittest.TestCase):
    def setUp(self):
        self.alpha = 0.5
        self.beta = 0.5
        self.thresholds = (5, 3)
        self.mckenna = McKennaMethod(self.alpha, self.beta, self.thresholds)

    def test_mckenna_model_update(self):
        frame_1 = np.random.rand(360, 640, 3).astype(np.float32) * 255
        frame_2 = np.random.rand(360, 640, 3).astype(np.float32) * 255

        with patch('numpy.gradient', return_value=[np.zeros_like(frame_1), np.zeros_like(frame_1)]):
            self.mckenna.process_one_frame(frame_1) 
            
        initial_mean = self.mckenna.mean_gaussian.copy()
        initial_variance = self.mckenna.variance_gaussian.copy()

        with patch('numpy.gradient', return_value=[np.zeros_like(frame_2), np.zeros_like(frame_2)]):
            self.mckenna.process_one_frame(frame_2)  

        self.assertNotEqual(np.all(initial_mean == self.mckenna.mean_gaussian), True)
        self.assertNotEqual(np.all(initial_variance == self.mckenna.variance_gaussian), True)


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