import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import logging
import os


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
# update model and label map paths
MODEL_DIR = os.path.join(PROJECT_DIR, 'models/ssd_mobilenet_v2_fpnlite_320x320_coco17_tpu-8/saved_model')
LABEL_MAP_PATH = os.path.join(PROJECT_DIR, 'models/research/object_detection/data/mscoco_complete_label_map.pbtxt')

# load TensorFlow model 
def load_tensorflow_model(model_directory):
    try:
        logging.info(f"Loading TensorFlow object detection model ssd_mobilenet_v2 trained on COCO from {model_directory}")
        model = tf.saved_model.load(model_directory)
        logging.info("The model was loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Error! Can not load TensorFlow model: {str(e)}")
        return None

# load TensorFlow detection model and category index
DETECTION_MODEL = load_tensorflow_model(MODEL_DIR)
CATEGORY_INDEX = label_map_util.create_category_index_from_labelmap(LABEL_MAP_PATH, use_display_name=True)

# References:
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html#tensorflow-installation
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html#tensorflow-object-detection-api-installation
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html#coco-api-installation
# https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/auto_examples/index.html#examples
# https://www.tensorflow.org/api_docs/python/tf/saved_model/load
# https://www.tensorflow.org/api_docs/python/tf/compat/v1/saved_model/load
# https://www.tensorflow.org/guide/saved_model
# https://stackoverflow.com/questions/51569669/python-from-utils-import-label-map-util-importerror-cannot-import-name-lab
# https://github.com/tensorflow/models/issues/1990
# https://guides.co/g/object-detection-tutorial-in-tensorflow-real-time-object-detection/151695
# https://kitflix.com/python-code-for-object-detection-using-tensorflow/
# https://www.tensorflow.org/tutorials/keras/save_and_load
# https://www.projectpro.io/recipes/load-tensorflow-model



""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""