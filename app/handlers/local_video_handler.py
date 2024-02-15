from config import VIDEO_DIRECTORY
import shutil
import os
import logging

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

# saves motion event video file in local folder 
def save_video_in_local_directory(video_path_source):
    if video_path_source is None:
        logging.error("Video path was not provided for local saving.")
        return None

    # gets file name 
    video_file_name = os.path.basename(video_path_source)

    # creates local path
    local_path_for_video = os.path.join(VIDEO_DIRECTORY, video_file_name)

    try:
        # moves file to the path
        shutil.move(video_path_source, local_path_for_video)
    except Exception as e:
        logging.error(f"Error! Could not save video on local storage: {e}")
        return None

    return local_path_for_video

# References:
# https://docs.python.org/3/library/os.path.html
# https://github.com/h5py/h5py/issues/1220
# https://docs.python.org/3/library/shutil.html
# https://www.geeksforgeeks.org/python-shutil-move-method/
# https://stackoverflow.com/questions/8858008/how-do-i-move-a-file-in-python
# https://www.geeksforgeeks.org/python-os-path-basename-method/
# https://stackoverflow.com/questions/33372054/given-a-path-how-can-i-extract-just-the-containing-folder-name

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """