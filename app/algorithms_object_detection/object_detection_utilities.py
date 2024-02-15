import os
import cv2
import time
from datetime import datetime
import numpy as np
import tensorflow as tf
import logging

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """


# classifying objects
OBJECT_TYPE_CLASS_NAME = {
    "person": "Human",
    "dog": "Animal",
    "cat": "Animal"
}
COLOR_CONVERSION = cv2.COLOR_BGR2RGB
RECT_COLOR = (0, 0, 255)  # red color in BGR
RECT_THICKNESS = 2  # rectangle border thickness
WARMUP_FRAMES = 2  # skippped frames during camera "warm-up"
IMG_PROCESSING_INTERVAL = 1  # image processing interval
SLEEP_TIME = 0.01  # sleep lengh (seconds) between batch processing 
processed_images = set() # to keep track of processed images 

# handles object recognition 
def object_recognition(frame, detection_model, category_index, detection_threshold):
    # verifies that input frame is valid
    if frame is None or not isinstance(frame, np.ndarray):
        # if frame is not valid, returns original frame and an empty list 
        return frame, []

    # verifies that detection model is loaded
    if detection_model is None:
        # if the detection model is not loaded, returns original frame 
        return frame

    try:
        # converts frame to RGB format and uint8 data type 
        frame_processed = cv2.cvtColor(frame, COLOR_CONVERSION)
        frame_processed = frame_processed.astype(np.uint8)

        # converts frame to a TensorFlow tensor
        tf_input_tensor = tf.convert_to_tensor([frame_processed], dtype=tf.uint8)

        # object detection on processed frame
        object_detections = detection_model(tf_input_tensor)

        # filters specified classes (person, dog etc.)
        filtered_results = []
        for i in range(len(object_detections['detection_boxes'][0])):
            score = object_detections['detection_scores'][0][i]
            if score > detection_threshold:
                class_id = int(object_detections['detection_classes'][0][i])
                class_name = category_index[class_id]['name']
                if class_name in OBJECT_TYPE_CLASS_NAME:
                    object_type = OBJECT_TYPE_CLASS_NAME[class_name]
                    bounding_box = object_detections['detection_boxes'][0][i]
                    
                    # filtered detection are appended to the list
                    filtered_results.append({
                        'class_name': class_name,
                        'object_type': object_type,
                        'score': score,
                        'bounding_box': bounding_box
                    })
        
        # draws bounding boxes on the original frame 
        frame_with_detections_boxes_labels = draw_boxes_labels_on_detections(frame, filtered_results)

        # returns frame with bounding boxes around detected objects and list of detected object (class, type, score..)
        return frame_with_detections_boxes_labels, filtered_results
    except Exception as e:
        # logs an error message
        logging.error(f"Error while running object recognition: {str(e)}")

        # if error, returns original frame and an empty list 
        return frame, []


def draw_boxes_labels_on_detections(np_image, object_detections):
    # variables for labels
    label_font  = cv2.FONT_HERSHEY_SIMPLEX
    label_font_scale = 0.6
    label_font_color = (0, 0, 255)  # red color 
    line = 2

    for detection in object_detections:
        box = detection['bounding_box']
        object_type = detection['object_type']  # gets type of detected object based on classification

        y_min, x_min, y_max, x_max = box
        height_image, width_image, _ = np_image.shape
        starting_point = (int(x_min * width_image), int(y_min * height_image))
        ending_point = (int(x_max * width_image), int(y_max * height_image))

        # draws bounding rect on the image
        np_image = cv2.rectangle(np_image, starting_point, ending_point, RECT_COLOR, RECT_THICKNESS)

        # label location in the top left corner on top of the bounding box 
        label_location = (starting_point[0], starting_point[1] - 10)

        # Put the label text on the image
        cv2.putText(np_image, object_type, label_location, label_font ,label_font_scale, label_font_color, line)
    
    # returns image with bounding boxes/labels drawn around detected objects
    return np_image


# performs image processing in it's own thread to help with video lag
def perform_image_processing_in_thread(video_camera_instance, path_for_saving_raw_images, path_for_saving_processed_image, detection_model, category_index, detection_threshold):
    # initialize frame counter
    counter = 0

    # set video_camera_warmup to True
    video_camera_warmup = True

    while True:
        try:
            current_time = time.time()

            if video_camera_warmup:
                # skip frames until warmup frames threshold is reached
                if counter >= WARMUP_FRAMES:
                    video_camera_warmup = False   # finished warmup 
                counter += 1
                continue # skip frame during warmup

            if current_time - video_camera_instance.last_processed_time >= IMG_PROCESSING_INTERVAL:
                for raw_image_name in sorted(os.listdir(path_for_saving_raw_images)):
                    counter += 1

                    image_path_raw = os.path.join(path_for_saving_raw_images, raw_image_name)

                    # verify if image was processed
                    if image_path_raw in processed_images:
                        continue

                    frame = cv2.imread(image_path_raw)

                    if frame is not None and isinstance(frame, np.ndarray):
                        # do object detection on the frame
                        frame_processed, _ = object_recognition(frame, detection_model, category_index, detection_threshold)

                         # save processed frame in a folder
                        image_name_processed = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        image_path_processed = os.path.join(path_for_saving_processed_image, image_name_processed)
                        cv2.imwrite(image_path_processed, frame_processed)
                

                        # adds processed image to the set
                        processed_images.add(image_path_raw)

                    video_camera_instance.last_processed_time = current_time

            # sleep before processing next batch 
            time.sleep(SLEEP_TIME)
        except Exception as e:
            logging.error(f"Error in the image processing thread: {str(e)}")
            break

# References:
# https://github.com/tensorflow/models/blob/master/research/object_detection/configs/tf2/ssd_mobilenet_v2_320x320_coco17_tpu-8.config
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/object_detection_camera.html
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model_tf1.html
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_saved_model.html
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/plot_object_detection_checkpoint.html
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html#coco-api-installation
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html#install-the-object-detection-api
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/
# https://github.com/tensorflow/tensorflow/issues/62135
# https://stackoverflow.com/questions/73326997/output-dictdetection-boxes-keyerror-detection-boxes
# https://realpython.com/intro-to-python-threading/
# https://www.pythontutorial.net/python-concurrency/python-threading/
# https://docs.python.org/3/library/threading.html
# https://forum.opencv.org/t/help-needed-on-understanding-why-video-from-webcam-is-lagging-when-using-thread-and-queue/13064
# https://dev.to/seracoder/a-comprehensive-guide-to-python-threading-advanced-concepts-and-best-practices-3p9c
# https://www.python-engineer.com/courses/advancedpython/16-threading/
# https://www.python-engineer.com/courses/advancedpython/16-threading/
# https://www.python-engineer.com/courses/advancedpython/16-threading/
# https://www.dataquest.io/blog/multithreading-in-python/
# https://www.dataquest.io/blog/multithreading-in-python/
# https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html
# https://github.com/blakeblackshear/frigate/issues/9651
# https://stackoverflow.com/questions/47242183/customizing-tf-object-detection-bounding-box-thickness-label-font-size
# https://github.com/ultralytics/yolov5/issues/6935
# https://de.mathworks.com/help/vision/ref/insertobjectannotation.html
# https://albumentations.ai/docs/getting_started/bounding_boxes_augmentation/
# https://github.com/tensorflow/models/issues/10561
# https://stackoverflow.com/questions/46051174/how-to-choose-coordinates-of-bounding-boxes-for-object-detection-from-tensorflow
# https://developer.arm.com/documentation/102557/2108/Object-detection-application-code-overview/Draw-the-bounding-boxes
# https://carla.readthedocs.io/en/latest/tuto_G_bounding_boxes/
# https://github.com/ultralytics/ultralytics/issues/4827
# https://albumentations.ai/docs/examples/example_bboxes2/
# https://github.com/ultralytics/yolov5/issues/6667
# https://github.com/roboflow/supervision/issues/365
# https://forum.opencv.org/t/opencv-box-not-showing-up-in-opencv-for-image-detection-or-realtime-detection/10583
# https://www.researchgate.net/profile/Sidra-Mehtab/publication/343282935_Object_Detection_and_Tracking_Using_OpenCV_in_Python/links/5f21672b299bf134048f8907/Object-Detection-and-Tracking-Using-OpenCV-in-Python.pdf
# https://www.programiz.com/python-programming/methods/built-in/set
# https://note.nkmk.me/en/python-opencv-bgr-rgb-cvtcolor/
# https://www.geeksforgeeks.org/python-opencv-cv2-cvtcolor-method/
# https://github.com/tensorflow/models/issues/4682
# https://github.com/tensorflow/models/blob/master/research/object_detection/utils/visualization_utils.py
# https://github.com/tensorflow/models/tree/master/research/object_detection
# https://github.com/tensorflow/models/tree/master
# https://www.tensorflow.org/hub/tutorials/object_detection

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """
