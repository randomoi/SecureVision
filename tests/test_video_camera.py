import unittest
from unittest.mock import patch, MagicMock
from app.camera.camera import VideoCamera
import numpy as np

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class TestVideoCamera(unittest.TestCase):

    def setUp(self):
        self.video_camera = VideoCamera(app=MagicMock(), user_id=1, motion_detection_mode='mgo2')
        self.video_camera.video_file_name = 'test_some_video.mp4'
        
    @patch('cv2.VideoCapture')
    def test_initialize_camera(self, mocked_video_capture):
        mocked_video_capture.return_value.isOpened.return_value = True
        self.video_camera._initialize_camera()
        self.assertTrue(self.video_camera.cap.isOpened())
        mocked_video_capture.assert_called_once_with(0)
        
        
    @patch('cv2.VideoCapture.isOpened', return_value=True)
    def test_initialize_camera2(self, mocked_is_opened):
        self.video_camera._initialize_camera()
        self.assertTrue(mocked_is_opened.called)  
        self.assertIsNotNone(self.video_camera.cap)  

    def test_start_stop_live_feed(self):
        with patch('cv2.VideoCapture.isOpened', return_value=True):
            self.video_camera._start_live_feed()  
            self.assertTrue(self.video_camera._is_live_feed_turned_on())  

        self.video_camera._stop_live_feed()  
        self.assertFalse(self.video_camera._is_live_feed_turned_on())  

    def test_initialize_motion_detection_frames(self):
        fake_frame = np.zeros((640, 360), dtype=np.uint8)
        self.video_camera._setup_motion_detection_frames(fake_frame)  
        self.assertIsNotNone(self.video_camera.previous_frame)  
        self.assertIsNotNone(self.video_camera.previous_frame_1)  
        self.assertIsNotNone(self.video_camera.previous_frame_2)  


    @patch('cv2.VideoCapture.read')
    def test_get_frame(self, mock_video_cap_read):
        fake_frame = np.zeros((640, 360, 3), dtype=np.uint8)
        mock_video_cap_read.return_value = (True, fake_frame)

        self.video_camera.camera_on = True
        self.video_camera._initialize_camera()

        frame, _ = self.video_camera.retrieve_frame()

        self.assertIsNotNone(frame)


    @patch('cv2.imwrite')
    def test_save_motion_detected_image(self, mock_imwrite):
        fake_frame = np.zeros((640, 360, 3), dtype=np.uint8)
        self.video_camera._save_motion_detected_image(fake_frame)

        mock_imwrite.assert_called()

    def test_detect_motion_manage_recording(self):
        fake_frame = np.zeros((640, 360, 3), dtype=np.uint8)
        dummy_mask = np.zeros((640, 360), dtype=np.uint8)

        motion_detected = self.video_camera._detect_motion_and_manage_recording(dummy_mask, fake_frame)
        self.assertFalse(motion_detected) 
         
    def test_pre_record_buffer(self):
        fake_frame = np.zeros((640, 360, 3), dtype=np.uint8)

        for _ in range(50):  
            self.video_camera._handle_pre_record_buffer(fake_frame)

        self.assertEqual(len(self.video_camera.pre_record_motion_buffer), self.video_camera.SIZE_OF_PRE_RECORD_BUFFER)

    @patch('cv2.VideoCapture.read')
    def test_gets_frame_no_camera(self, mock_video_cap_read):
        self.video_camera.camera_on = False
        frame, motion_data = self.video_camera.retrieve_frame()
        self.assertIsNone(frame)
        self.assertIsNone(motion_data)

    @patch('cv2.VideoCapture.read', return_value=(False, None))
    def test_get_failed_frame_reading(self, mock_video_cap_read):
        self.video_camera.camera_on = True
        frame, motion_data = self.video_camera.retrieve_frame()
        self.assertIsNone(frame)
        self.assertIsNone(motion_data)


    @patch('cv2.imwrite')
    def test_save_motion_detection_image(self, mock_imwrite):
        fake_frame = np.zeros((640, 480, 3), dtype=np.uint8)
        self.video_camera._save_motion_detected_image(fake_frame)
        mock_imwrite.assert_called()



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