import unittest
import numpy as np
from app.algorithms_object_detection.object_detection_utilities import object_recognition, draw_boxes_labels_on_detections  
from unittest.mock import MagicMock, patch

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class TestObjectDetection(unittest.TestCase):
    def setUp(self):
        self.sample_frame = np.random.randint(0, 255, (640, 480, 3), dtype=np.uint8)
        self.detection_model = MagicMock()
        self.category_index = {1: {'name': 'person'}, 2: {'name': 'cat'}, 3: {'name': 'dog'}}
        self.detection_threshold = 0.6

        self.mocked_detections = {
            'detection_boxes': np.array([[0.1, 0.4, 0.6, 0.7], [0.5, 0.7, 0.8, 0.9]]),
            'detection_scores': np.array([0.8, 0.5]),
            'detection_classes': np.array([1, 3])
        }
        
        self.detection_model.return_value = self.mocked_detections
        
    def test_detect_objects_for_valid_input(self):
        result_frame, detections = object_recognition(
            self.sample_frame, self.detection_model, self.category_index, self.detection_threshold)

    def test_detect_objects_for_invalid_frame(self):
        frame = None
        detection_model = MagicMock()
        category_index = {}
        detection_threshold = 0.5
        
        result_frame, detections = object_recognition(frame, detection_model, category_index, detection_threshold)
        
        self.assertIsNone(result_frame)
        self.assertEqual(detections, [])


    def test_empty_draw_detections(self):
        image_np = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = []
        result_image = draw_boxes_labels_on_detections(image_np, detections)
        self.assertTrue(np.array_equal(image_np, result_image))


    def test_detect_objects_no_detections_above_thresh(self):
        detection_model = MagicMock()
        detection_model.return_value = {
            'detection_boxes': np.array([[0.1, 0.2, 0.3, 0.4]]),
            'detection_scores': np.array([0.4]), 
            'detection_classes': np.array([1])
        }
        result_frame, detections = object_recognition(self.sample_frame, detection_model, self.category_index, self.detection_threshold)
    
        self.assertEqual(len(detections), 0)


    def test_exception_handling(self):
        detection_model = MagicMock(side_effect=Exception("Test Exception"))
    
        with self.assertLogs(level='ERROR'):
            result_frame, detections = object_recognition(self.sample_frame, detection_model, self.category_index, self.detection_threshold)
        
        self.assertIsNotNone(result_frame)  
        self.assertEqual(len(detections), 0)  


class TestProcessingImagesInThread(unittest.TestCase):
    @patch('app.algorithms_object_detection.object_detection_utilities.time') 
    @patch('app.algorithms_object_detection.object_detection_utilities.os.listdir')  
    def test_processing_images_in_thread(self, mock_listdir, mock_time):
        mock_listdir.return_value = ['image1.jpg', 'image2.jpg']
        pass


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