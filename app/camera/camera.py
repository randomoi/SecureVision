import os
import cv2
import time
from datetime import datetime 
from app.tensorFlow.tf_model_utilities import DETECTION_MODEL, CATEGORY_INDEX
from config import PATH_FOR_SAVING_PROCESSED_IMAGE, PATH_FOR_SAVING_IMAGE, VIDEO_DIRECTORY
from app.email_notifications.email_token_bucket import TokenBucket
from app.computer_vision.motion_analysis_utilities import process_and_buffer_motion_data, get_detection_mode_for_user, process_initial_frame, convert_frame_to_jpeg
from app.algorithms_motion_detection.mckenna_method import McKennaMethod
from app.algorithms_motion_detection.lukas_kanade_orb_method import LukasKanadeOrb
from app.computer_vision.motion_detection_processor import ModeProcessor
import pyaudio
import wave
import subprocess
import threading
import logging


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

class VideoCamera(object):
    # video constants
    FOURCC = cv2.VideoWriter_fourcc(*'avc1')
    VIDEO_WIDTH = 640
    VIDEO_HEIGHT = 360
    VIDEO_FPS = 30.0
    
    # thresholds constants
    MEDIAN_BLUR_VALUE = 5
    WARM_UP_PERIOD = 5
    HISTORY_VALUE = 400
    VAR_THRESHOLD = 40
    
    MOTION_DETECTION_THRESHOLD = 2.0
    DETECTION_THRESHOLD = 0.4
    
    THRESHOLD_WIDTH_RELATIVE = 0.005
    THRESHOLD_HEIGHT_RELATIVE = 0.005
    FRAMES_SINCE_RESET_MAX_VALUE = 300
  
    # intervals constants
    RECORDING_DURATION = 20.0
    IMAGE_INTERVAL_SAVING = 20

    MGO2_MODE = "mgo2"
    LUCAS_KANADE_ORB_MODE = "lucas_kanade_orb"
    MCKENNA_MODE = "mckenna"
    
    # date/time constants
    DATE_FORMAT = '%Y%m%d'
    TIME_FORMAT = '%H%M%S'
    TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'  
    
    # file extensions constants
    IMAGE_EXTENSION = '.jpg'
    MP4_EXTENSION = ".mp4"
    WAV_EXTENSION = "_raw.wav"
    MP4_COMBINED = "_combined.mp4"
    
    # audio constants
    AUDIO_SAMPLE_RATE = 44100
    AUDIO_CHUNK_SIZE = 1024

    CONTOUR_AREA_MIN = 10
    CONTOUR_THRESHOLD = 127  # for binary image conversion
    CONTOUR_COLOR = (0, 255, 0)  # for contour drawing
    CONTOUR_THICKNESS = 3 
    BINARY_VALUE_MAX = 255  # maximum value for binary images
    LUCAS_KANADE_PARAMETERS = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 15, 0.02))
    
    # paths
    PATH_FOR_SAVING_IMAGE = PATH_FOR_SAVING_IMAGE
    PATH_FOR_SAVING_PROCESSED_IMAGE = PATH_FOR_SAVING_PROCESSED_IMAGE
        
    def __init__(self, app, user_id, motion_detection_mode=None, credentials=None):   
        # context and state
        self.app, self.user_id, self.credentials = app, user_id, credentials
        self.camera_on, self.is_video_recording, self.video_recording_complete = False, False, False
        self.video_file_name, self.recording_start_time = None, None
        self.last_saved_image_time, self.last_processed_time = 0, time.time()

        # camera and recording settings
        self.cap, self.out, self.lock = None, None, threading.Lock()
        self.mgo2_background_subtractor = cv2.createBackgroundSubtractorMOG2(history=self.HISTORY_VALUE, varThreshold=self.VAR_THRESHOLD, detectShadows=False)
        self.MOTION_INTERVAL, self.SIZE_OF_PRE_RECORD_BUFFER = 20, 40  
        self.video_camera_start_time = time.time()

        # motion detection and processing
        self.frames_after_reset, self.initial_frame = 0, None
        self.previous_frame, self.previous_frame_1, self.previous_frame_2, self.previous_points = None, None, None, None
        self.motion_detected, self.not_logged_motion = False, False
        self.events_motion_buffer, self.pre_record_motion_buffer = [], []
        
        self.previous_detection_mode = None  
        self.rate_limiting_token_bucket = TokenBucket(5, 1/20)  # for rate limiting
        
        # object detection
        self.detection_model = DETECTION_MODEL  # pre-loaded TensorFlow detection model
        self.category_index = CATEGORY_INDEX  # pre-loade TensorFlow category index for detection model
        
        # modes
        self.motion_detection_mode = motion_detection_mode or get_detection_mode_for_user(app, user_id)
        
        # lukas kanade-orb method for motion detection
        self.lucas_kanade_orb_detection_tracking = LukasKanadeOrb(
            points_of_interest_detector=cv2.ORB_create(),
            lucas_kanade_parameters=self.LUCAS_KANADE_PARAMETERS,
            motion_detection_threshold=self.MOTION_DETECTION_THRESHOLD  
        )
        
        # mckenna method for motion detection
        self.mckenna_background_subtractor = McKennaMethod()  
        
        # mode processor for handling diff modes
        self.mode_processor = ModeProcessor(
            mgo2_background_subtractor=self.mgo2_background_subtractor,
            lucas_kanade_orb_detection_tracking=self.lucas_kanade_orb_detection_tracking,
            mckenna_background_subtractor=self.mckenna_background_subtractor,
            detection_model=self.detection_model,
            category_index=self.category_index,
            detection_threshold=self.DETECTION_THRESHOLD
        )
        
        # video and sound processing 
        self.video_processing_state = 'idle'
        self.video_ready_threading_event = threading.Event()
        self.sound_format = pyaudio.paInt16 
        self.chunk_size = self.AUDIO_CHUNK_SIZE
        
        # paths
        self.path_for_saving_image = PATH_FOR_SAVING_IMAGE
        self.path_for_saving_processed_image = PATH_FOR_SAVING_PROCESSED_IMAGE
   
        
    def _initialize_camera(self):  
        if self.cap is not None:  # check if camera is initialized
            return  
        try:
            self.cap = cv2.VideoCapture(0) # create a VideoCapture object 
            if not self.cap.isOpened():  # check if camera was opened
                logging.error("Camera was not found.")
            else:
                self.camera_initialized = True  # sets flag that camera is initialized            
        except Exception as e:
            raise RuntimeError(f"Error with camera initialization: {str(e)}")

    # checks current camera status 
    def _is_live_feed_turned_on(self):
        return self.camera_on

    # checks if the camera object is initialized/opened
    def _is_video_camera_initialized(self):
        return self.cap and self.cap.isOpened()

    def _read_from_video_camera(self):
        try:
            return self.cap.read() # read a frame 
        except Exception as e:
            return None, None # returns None to show that frames can not be read  

    def _release_video_camera(self):
        # checks if camera is initialized before releasing
        if self._is_video_camera_initialized():
            try:
                self.cap.release() # release camera 
            except Exception as e:
                logging.error(f"Error releasing video camera: {str(e)}")
            finally:
                self.cap = None # set camera object to None after releasing
 
    def _start_video_recording(self):
        with self.lock:
            # check if is not already recording
            if not self.is_video_recording:
                self.is_video_recording = True 
                self.video_recording_complete = False  # reset the flag
                # holds start time of recording
                self.recording_start_time = time.time()
                timestamp = datetime.now().strftime(self.DATE_FORMAT + '_' + self.TIME_FORMAT)
                video_name = f'video_{timestamp}{self.MP4_EXTENSION}'
                self.video_file_name = f'{VIDEO_DIRECTORY}/{video_name}'
                self.out = cv2.VideoWriter(self.video_file_name, self.FOURCC, self.VIDEO_FPS, (self.VIDEO_WIDTH, self.VIDEO_HEIGHT))  
                
                self._start_sound_recording() # starts sound recording
            
    def _start_sound_recording(self):
        try:
            # initialize PyAudio 
            p = pyaudio.PyAudio()

            # get default input device index
            self.input_device_index = p.get_default_input_device_info()['index']
            logging.info(f"Input device index: {self.input_device_index}")

            # get/set sample rate and channels dynamically based on device abilities
            device_information = p.get_device_info_by_index(self.input_device_index)
            self.sample_rate = int(device_information['defaultSampleRate'])
            self.number_of_channels = device_information['maxInputChannels']
            # sets chunk size 
            self.chunk_size = self.AUDIO_CHUNK_SIZE

            # open sound stream 
            self.sound_stream = p.open(
                format=pyaudio.paInt16,  
                channels=self.number_of_channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk_size
            )

            # sets flag to true
            self.is_video_recording = True
            logging.info("sound stream opened.")

        except Exception as e:
            # set flag to false 
            self.is_video_recording = False
            logging.error(f"Error opening sound stream: {e}", exc_info=True)

        # creates sound frames list
        self.sound_frames = []

        # in a separate thread starts sound recording loop 
        self._sound_recording_thread = threading.Thread(target=self._process_audio_input)
        self._sound_recording_thread.start()


    def _process_audio_input(self):
        try:
            # read sound frames during recording 
            while self.is_video_recording:
                try:
                    # read sound frame from sound stream
                    sound_frame = self.sound_stream.read(self.chunk_size, exception_on_overflow=False)
                    # add read sound frame to list of sound frames
                    self.sound_frames.append(sound_frame)
                except IOError as e:
                    raise IOError(f"Error reading sound frame: {e}")
        except Exception as e:
            self.is_video_recording = False  # stop loop
            logging.error(f"Error in process_audio_input: {e}")

    def _stop_recording(self):
        sound_video_merged_file = None  
        try:
            with self.lock:
                if not self.is_video_recording:
                    return None

                self.is_video_recording = False  # stop recording

                # release video recording 
                if self.out:
                    self.out.release()
                    self.out = None

                # stop and close sound stream
                if self.sound_stream:
                    self.sound_stream.stop_stream()
                    self.sound_stream.close()
                    self.sound_stream = None

                    # pause for sound recording thread to finalize
                    if hasattr(self, '_sound_recording_thread'):
                        self._sound_recording_thread.join()

                    # save sound frames to WAV file 
                    if self.sound_frames:
                        raw_sound_file_name = self.video_file_name.replace(self.MP4_EXTENSION, self.WAV_EXTENSION)
                        try:
                            with wave.open(raw_sound_file_name, 'wb') as wf:
                                wf.setnchannels(self.number_of_channels)
                                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.sound_format))
                                wf.setframerate(self.sample_rate)
                                wf.writeframes(b''.join(self.sound_frames))
                        except Exception as e:
                            logging.error(f"Failed to save sound frames: {e}")
                            return None, {"error": f"Failed to save sound frames: {e}"}

                    # combine sound and video files
                    try:
                        sound_video_merged_file = self._merge_sound_and_video(raw_sound_file_name)
                    except Exception as e:
                        logging.error(f"Error: Did not combine sound and video: {e}")
                        return None, {"error": f"Did not combine sound and video: {e}"}

                self.video_recording_complete = True  # marks recording as finished
        except Exception as e:
            logging.error(f"Error! Stopping recording: {e}")
            return None, {"error": f"Error! Stopping recording: {e}"}

        return sound_video_merged_file, None  # returns file or None 


    def _merge_sound_and_video(self, raw_sound_file_name):
        # updates video processing state to show the process started
        self.video_processing_state = 'processing'

        # create merged file 
        merged_video_file_name = self.video_file_name.replace(self.MP4_EXTENSION, self.MP4_COMBINED)

        # verify if sound file exists
        if raw_sound_file_name:
            # using ffmpeg prepare to merge sound and video 
            ffmpeg_cmd = ['ffmpeg', '-i', self.video_file_name, '-i', raw_sound_file_name,
                            '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
                            merged_video_file_name]
            try:
                # run ffmpeg command to merge sound and video
                subprocess.run(ffmpeg_cmd, check=True)
                
                # update state to show the video is ready
                self.video_processing_state = 'ready'
                self.video_ready_threading_event.set()
            
                try:
                    os.remove(raw_sound_file_name) # delete raw sound file 
                except OSError as e:
                    logging.warning(f"Error! File {raw_sound_file_name} not found for deletion: {e}")

                try:
                    os.remove(self.video_file_name) # delete original video file
                except OSError as e:
                    logging.warning(f"Error! Original video file {self.video_file_name} not found for deletion: {e}")
                    
                
            except subprocess.CalledProcessError as e:
                logging.error("Error! Failed to merge sound and video: {}".format(e))
                self.video_processing_state = 'error'
                return None

        else:
            # update state to show error 
            self.video_processing_state = 'error'
            logging.error("No sound file was provided for merging.")

        # return merged file
        return merged_video_file_name

                
    def _start_live_feed(self):
        if not self.camera_on: # checks if camera is off
            self.camera_on = True # turn camera on
            self._initialize_camera() # initialize camera
            
            # checks if camera is opened
            if not (self.cap and self.cap.isOpened()):
                logging.error("Error! Failed to start live feed.")
        else:
            logging.error("Error! Live feed has alredy started.")

    def _stop_live_feed(self):
        if self.camera_on: # check if camera is on
            self.camera_on = False # turn camera off
            self._release_video_camera() # release video camera

    def _save_frame_to_video(self, ret, frame):
        # checks if currently recording and frame was read 
        if self.is_video_recording and ret:
            # check if video writer is initialized
            if self.out is not None:
                # write current frame to file
                self.out.write(frame)
                # calculates elapsed time since recording started
                elapsed_time = time.time() - self.recording_start_time
                # checks if recording time > 10 secs if yes, stops recording 
                if elapsed_time > 10.0:  
                    self._stop_recording()

    # gets file path for merged sound and video file
    def get_current_final_video_path(self):
        if not self.video_recording_complete or self.video_processing_state != 'ready':
            logging.error("Video is not ready or recording did not finish.")
            return None

        merged_video_file_name = self.video_file_name.replace(self.MP4_EXTENSION, self.MP4_COMBINED)
        return merged_video_file_name

 
    def setup_motion_detection_mode(self, mode):
        # define availble detection modes 
        AVAILABLE_DETECTION_MODES = ["mgo2", "lucas_kanade_orb", "mckenna"]
        
        # verify if valid mode
        if mode in AVAILABLE_DETECTION_MODES:
            # sets detection mode
            self.motion_detection_mode = mode
        else:
            logging.error(f"Error! Invalid detection mode: {mode}")


    def retrieve_frame(self):       
        # verify/initialize camera, if not initialized or live feed is off returns none
        if not self._initialize_and_verify_video_camera():
            return None, None

        current_time = time.time() # save current time

        # verify if camera is warming up
        if current_time - self.video_camera_start_time < self.WARM_UP_PERIOD:
            ret, frame = self._read_from_video_camera()
            # returns frame without motion data during warmup phase
            return convert_frame_to_jpeg(frame, None)  

        # reads frame from video camera
        ret, frame = self._read_from_video_camera()
        if not ret:
            return None, None

        # converts to grayscale and applies gaussian blur
        frame, gray_frame = process_initial_frame(frame)
        
        # adds current frame to pre-record buffer
        self._handle_pre_record_buffer(frame)

        # setup motion detection frames 
        if self.previous_frame_2 is None:
            self._setup_motion_detection_frames(gray_frame)
            # returns none if previous frames are not initialized
            return None, None  

        # changes in detection mode when it changes
        if self.previous_detection_mode != self.motion_detection_mode:
            self.previous_detection_mode = self.motion_detection_mode

        # motion detection based on current mode
        if self.motion_detection_mode == self.MGO2_MODE:
            motion_data = self.mode_processor.process_mgo2_and_three_frame_diff_mode(
                gray_frame, self.previous_frame_1, self.previous_frame_2, self._detect_motion_and_manage_recording, frame
            )

        elif self.motion_detection_mode == self.LUCAS_KANADE_ORB_MODE:
            motion_data = self.mode_processor.process_lucas_kanade_orb_and_three_frame__diff_mode(
                gray_frame, frame, self.previous_frame, self.previous_frame_1, self.previous_frame_2, 
                self._detect_motion_and_manage_recording, self.video_camera_start_time, self.WARM_UP_PERIOD
            )

        elif self.motion_detection_mode == self.MCKENNA_MODE:
            motion_data = self.mode_processor.process_mckenna_and_three_frame_diff_mode(
                gray_frame, frame, self.previous_frame_1, self.previous_frame_2, self._detect_motion_and_manage_recording
            )

        else:
            logging.error(f"Error! Detection mode is unknown: {self.motion_detection_mode}")
          
        # if recording, save current frame to video stream 
        self._save_frame_to_video(ret, frame)
        # if nececsary, reset motion detection frames 
        self._reset_frames_if_necessary()
        # updates motion detection frames
        self._update_frames_for_motion_detection(gray_frame)
        
        # returns converted frame to JPEG with motion data
        return convert_frame_to_jpeg(frame, motion_data)

    
    def _initialize_and_verify_video_camera(self):
        # verify if live feed is on
        if not self._is_live_feed_turned_on():
            return False 

        # verify if camera was initialized
        if not self._is_video_camera_initialized():
            # if not initialized, initialize
            self._initialize_camera()
        return True  # camera is ready 
        
    def _setup_motion_detection_frames(self, current_frame):
        # sets last three frames to current gray_frame frame
        self.previous_frame_2 = current_frame
        self.previous_frame_1 = current_frame
        self.previous_frame = current_frame

    def _update_frames_for_motion_detection(self, current_frame):
        # current frame is new previous frame and older frames are shifted back 
        self.previous_frame_2 = self.previous_frame_1
        self.previous_frame_1 = self.previous_frame
        self.previous_frame = current_frame

    def _handle_pre_record_buffer(self, frame):
        # adds current frame to pre-record buffer
        self.pre_record_motion_buffer.append(frame)

        # if buffer size > than limit, remove oldest frame
        if len(self.pre_record_motion_buffer) > self.SIZE_OF_PRE_RECORD_BUFFER:
            self.pre_record_motion_buffer.pop(0)

        
    def _detect_motion_and_manage_recording(self, combined_mask, frame):
        try:
            # set motion detection flag to False
            motion_detected = False  

            # verify if combined mask is None 
            if combined_mask is None:
                return motion_detected  
            
            current_time = time.time()  # save current time 

            # do motion detection at pre-defined intervals 
            if self.frames_after_reset % self.MOTION_INTERVAL == 0:
                # process combined mask to detect motion
                motion_detected = self._generate_combined_mask(combined_mask, frame)

                if motion_detected: # if motion is detected
                    # veirfy if not recording
                    if not self.is_video_recording:
                        # starts video recording
                        self._start_video_recording()
                      
                    # if current_time - last time image was saved is more than dynamic_image_saving_interval, saves frame
                    if current_time - self.last_saved_image_time > self.dynamic_image_saving_interval(motion_detected):
                        self._save_motion_detected_image(frame)
                        self.last_saved_image_time = current_time # updates time of last image was saved

                # if motion is not detected 
                elif self.is_video_recording:
                    # verifyies and stop recording based on elapsed time 
                    self._evaluate_and_stop_recording(current_time)

            return motion_detected

        except Exception as e:
            raise Exception(f"Error! An error in _detect_motion_and_manage_recording: {str(e)}")

    # interval is determined if substantial motion was detected recently
    def dynamic_image_saving_interval(self, motion_detected):
        return self.IMAGE_INTERVAL_SAVING / 2 if motion_detected else self.IMAGE_INTERVAL_SAVING

    def _save_motion_detected_image(self, frame):
        try:
            current_time = time.time() # get current time

            # create file name 
            motion_image_name = f"motion_detected_{datetime.now().strftime(self.TIMESTAMP_FORMAT)}{self.IMAGE_EXTENSION}"

            # path + image name to create full path
            image_path = os.path.join(self.PATH_FOR_SAVING_IMAGE, motion_image_name)

            # saves frame as an image at indicated path
            cv2.imwrite(image_path, frame)
            logging.debug(f"[_detect_motion_and_manage_recording] Saved image at: {image_path}")

            # update last saved image time
            self.last_saved_image_time = current_time

            # gets biggest contour from frame
            biggest_contour = self._get_biggerst_contour(frame)

            if biggest_contour is not None:
                # create sa dictionary with motion data
                motion_data = {
                    "x": biggest_contour[0],
                    "w": biggest_contour[2],
                    "frame_width": frame.shape[1],
                    "frame_height": frame.shape[0], 
                    "contour_area": biggest_contour[3],
                    "image_path": image_path
                }
                # process and buffer amotion data
                process_and_buffer_motion_data(self.events_motion_buffer, motion_data, self.user_id, self.app)
            else:
                logging.warning("Did not finde contour in frame.")

        except Exception as e:
            raise Exception(f"Error! Did not save image: {image_path}, Error: {e}")


    def _get_biggerst_contour(self, frame):
        # finds contours on gray_frame frame
        contours, _ = cv2.findContours(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:  # if contours found
            # find biggest contour 
            biggest_contour = max(contours, key=cv2.contourArea)

            # gets bounding box of biggest contour
            x, y, w, h = cv2.boundingRect(biggest_contour)
            # calculates counter area of biggest contour
            contour_area = cv2.contourArea(biggest_contour)

            # return bounding box + area of biggest contour
            return x, y, w, h, contour_area

        return None # if contours not found


    def _generate_combined_mask(self, combined_mask, frame):
        motion_detected = False # sets flag to False

        # if combined mask has three channels, convert to grayscale
        if len(combined_mask.shape) == 3 and combined_mask.shape[2] == 3:
            combined_mask = cv2.cvtColor(combined_mask, cv2.COLOR_BGR2GRAY)

        # transform combined mask to binary image 
        _, combined_mask = cv2.threshold(combined_mask, self.CONTOUR_THRESHOLD, self.BINARY_VALUE_MAX, cv2.THRESH_BINARY)

        # finds contours in binary image
        contours, _ = cv2.findContours(combined_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # filter contours with area less set minimum
        contours = [contour for contour in contours if cv2.contourArea(contour) >= self.CONTOUR_AREA_MIN]
        
        # if contours available after filtering
        if contours:
            # reset flag to show that motion was not logged
            self.not_logged_motion = False

            # find biggest contour 
            biggest_contour = max(contours, key=cv2.contourArea)
            # get bounding box of biggest contour
            x, y, w, h = cv2.boundingRect(biggest_contour)
            
            # get height and widht 
            frame_height, frame_width = frame.shape[:2]

            # check if movement is substantial 
            if self._is_substantial_movement(x, y, w, h, frame_width, frame_height):
                # draw rect around biggest contour
                cv2.rectangle(frame, (x, y), (x + w, y + h), (self.CONTOUR_COLOR), self.CONTOUR_THICKNESS)
                motion_detected = True # sets motion detected flag 

        return motion_detected # sets motion detected flag 

    def _evaluate_and_stop_recording(self, current_time):
        # calculates elapsed time since recording has started
        elapsed_time = current_time - self.recording_start_time
        
        # checks if elapsed time is > 20 secs
        if elapsed_time > self.RECORDING_DURATION:  
            # stop recording if yes 
            self._stop_recording()

    def _is_substantial_movement(self, x, y, w, h, frame_width, frame_height):
        # thresholds for substantial movement relative to frame 
        threshold_width_relative = self.THRESHOLD_WIDTH_RELATIVE  
        threshold_height_relative = self.THRESHOLD_HEIGHT_RELATIVE  

        # checks if width and height of motion > thresholds
        return (w > frame_width * threshold_width_relative) and \
            (h > frame_height * threshold_height_relative)

    def _reset_frames_if_necessary(self):
        self.frames_after_reset += 1 # increment counter 
        
        # checks if frames since last reset > set value
        if self.frames_after_reset > self.FRAMES_SINCE_RESET_MAX_VALUE:
            # reset initial frame to None, if yes
            self.initial_frame = None
            # reset counter
            self.frames_after_reset = 0

# References: 
# https://www.tutorialspoint.com/list-all-the-microphones-connected-to-system-in-python-using-pyaudio
# https://stackoverflow.com/questions/59371075/opencv-error-cant-open-camera-through-video-capture
# https://blog.miguelgrinberg.com/post/video-streaming-with-flask/page/8
# https://github.com/tiangolo/fastapi/discussions/6284
# https://superuser.com/questions/1782933/where-does-completed-file-go-by-default-when-merging-audio-and-video-files-toget
# https://discourse.psychopy.org/t/sound-and-movie-files-not-always-working/29538
# https://stackoverflow.com/questions/30619740/downsampling-wav-audio-file
# https://stackoverflow.com/questions/58207291/is-there-a-way-to-check-if-camera-is-connected-without-cap-cv2-videocapture
# https://github.com/AdaptiveMotorControlLab/Camera_Control/blob/master/camera_control_GUI.py
# https://github.com/r0x0r/pywebview/issues/403
# https://stackoverflow.com/questions/50128669/how-to-combine-2-video-files-and-audio-file-with-ffmpeg
# https://trac.ffmpeg.org/wiki/Encode/AAC
# https://superuser.com/questions/684955/converting-audio-to-aac-using-ffmpeg
# https://ffmpeg.org/ffmpeg.html
# https://stackoverflow.com/questions/59556761/how-to-start-and-stop-saving-video-frames-according-to-a-trigger-with-opencv-vid
# https://www.sololearn.com/en/Discuss/3023106/opencv-video-recording-problem
# https://discuss.streamlit.io/t/problem-with-displaying-a-recorded-video/3458
# https://github.com/Zulko/moviepy/issues/953
# https://pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/# https://stackoverflow.com/questions/15085348/what-is-the-use-of-join-in-threading
# https://forums.raspberrypi.com/viewtopic.php?t=65941
# https://github.com/cclaan/PyAudioNotebook/blob/master/PyAudio%20Demos.ipynb
# https://stackoverflow.com/questions/45025892/sound-generated-not-being-saved-to-a-file-as-it-should
# https://stackoverflow.com/questions/10733903/pyaudio-input-overflowed
# https://discourse.psychopy.org/t/rare-and-strange-conflict-between-sound-file-and-movie-file-with-ffmpeg/3906
# https://batchloaf.wordpress.com/2017/02/12/a-simple-way-to-read-and-write-audio-and-video-files-in-c-using-ffmpeg-part-2-video/
# https://forums.raspberrypi.com/viewtopic.php?t=71062
# https://www.linuxquestions.org/questions/programming-9/doing-a-record-in-python-with-a-microphone-hangs-the-thread-and-prevents-play-until-reboot-4175724557/
# https://discuss.python.org/t/error-in-opening-a-wav-file/39090
# https://community.rhasspy.org/t/no-audio-is-recorded-wakeword-works-fine/2274
# https://stackoverflow.com/questions/64927055/security-cam-stop-recording-after-there-is-no-motion-at-a-certain-timer
# https://github.com/opencv/opencv/issues/19527
# https://github.com/pyinstaller/pyinstaller/issues/8026
# https://github.com/ultralytics/yolov5/issues/12247
# https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html
# https://nrsyed.com/2018/07/05/multithreading-with-opencv-python-to-improve-video-processing-performance/
# https://discourse.slicer.org/t/how-to-load-the-image-streaming-from-opencv-to-2d-view/31756
# https://stackoverflow.com/questions/34122949/working-outside-of-application-context-flask
# https://github.com/ultralytics/yolov5/issues/2064
# https://stackoverflow.com/questions/62848221/how-to-wait-for-camera-to-initialize
# https://stackoverflow.com/questions/48025689/how-to-get-previous-frame-of-a-video-in-opencv-python
# https://stackoverflow.com/questions/10607688/how-to-create-a-file-name-with-the-current-date-time-in-python
# https://stackoverflow.com/questions/72446069/motion-detector-disregard-background-motion-incorrect-id
# https://github.com/motioneye-project/motioneye/issues/2417
# https://medium.com/geekculture/working-with-time-and-date-in-python-6cce748f90f5
# https://www.programiz.com/python-programming/datetime/current-time
# https://stackoverflow.com/questions/75037622/pyaudio-oserror-errno-9998-invalid-number-of-channels-on-mac-with-external
# https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html
# https://docs.opencv.org/3.4/df/d0d/tutorial_find_contours.html
# https://www.geeksforgeeks.org/find-and-draw-contours-using-opencv-python/
# https://pyimagesearch.com/2021/04/28/opencv-thresholding-cv2-threshold/
# https://docs.opencv.org/3.4/d8/d01/group__imgproc__color__conversions.html
# https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html
# https://stackoverflow.com/questions/8369547/checking-contour-area-in-opencv-using-python
# https://stackoverflow.com/questions/56736043/extract-building-edges-from-map-image-using-python
# https://stackoverflow.com/questions/59474010/unable-to-find-and-draw-biggest-contour
# https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html
# https://github.com/facebookresearch/maskrcnn-benchmark/issues/339
# https://medium.com/analytics-vidhya/opencv-findcontours-detailed-guide-692ee19eeb18
# https://docs.opencv.org/3.4/dc/dcf/tutorial_js_contour_features.html
# https://pyimagesearch.com/2021/04/28/opencv-color-spaces-cv2-cvtcolor/
# https://learnopencv.com/opencv-threshold-python-cpp/
# https://learnopencv.com/contour-detection-using-opencv-python-c/
# https://stackoverflow.com/questions/18870603/in-opencv-python-why-am-i-getting-3-channel-images-from-a-grayscale-image
# https://github.com/matterport/Mask_RCNN/issues/1644
# https://github.com/ultralytics/ultralytics/issues/948
# https://de.mathworks.com/matlabcentral/answers/126760-how-to-convert-a-binary-image-to-a-gray-scale-image
# https://www.enablegeek.com/tutorial/python-time-elapsed/
# https://stackoverflow.com/questions/3620943/measuring-elapsed-time-with-the-time-module
# https://www.thethingsnetwork.org/forum/t/after-resetting-frame-counters-payload-is-shown-on-gateway-traffic-but-not-in-application/19331
# https://github.com/Motion-Project/motion/discussions/1642
# https://github.com/blakeblackshear/frigate/discussions/8674
# https://github.com/blakeblackshear/frigate/issues/2863


""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""