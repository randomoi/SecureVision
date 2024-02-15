import os
import subprocess
import json
import logging

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

SUFFIX_COMBINED_VIDEO = "_combined.mp4"
SUFFIX_METADATA_VIDEO = "_merged_meta.mp4"
FFMPEG_EXEC = 'ffmpeg'
FFPROBE_EXEC = 'ffprobe'
JSON_FORMAT = 'json'
METADATA_TAG = 'comment'
LOG_LEVEL_ERROR = 'error'
SHOW_ENTRIES = '-show_entries'
FORMAT_TAGS = 'format_tags=comment'


def embed_metadata_on_video(video_path, metadata):
    # converts metadata dict to formatted JSON string
    metadata_formated = json.dumps(metadata)

    # new file name with '_merged_meta.mp4' ending
    output_file_name = video_path.replace(SUFFIX_COMBINED_VIDEO, SUFFIX_METADATA_VIDEO)

    # buld FFmpeg command for metadata embedding 
    command = [
        FFMPEG_EXEC,
        '-i', video_path,
        '-metadata', f'{METADATA_TAG}={metadata_formated}',
        '-codec', 'copy',
        output_file_name
    ]

    # runs command and get output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # delete original file after creating new file
    try:
        os.remove(video_path)
        logging.info(f"Deleted original file: {video_path}")
    except OSError as e:
        logging.error(f"Error! Can not delete original video file: {e}")
        return None  # returns None to show failure

    # verifies if metadata was correctly embedded
    check_embedded_metadata(output_file_name)

    # returns path of the video file with embedded metadata
    return output_file_name

def check_embedded_metadata(video_path):
    # build FFprobe command to extract metadata 
    command = [
        FFPROBE_EXEC,
        '-v', LOG_LEVEL_ERROR,
        SHOW_ENTRIES, FORMAT_TAGS,
        '-of', JSON_FORMAT,
        video_path
    ]
    # runs FFprobe command and gets result
    result = subprocess.run(command, capture_output=True, text=True)

    # checks if FFprobe execution was successful
    if result.returncode != 0:
        logging.error(f"Error! Can not verify metadata: {result.stderr}")
    else:
        # parses JSON output to extract embedded metadata
        metadata = json.loads(result.stdout)
        # gets embeded metadata
        metadata_embedded = metadata.get('format', {}).get('tags', {}).get('comment', ' Metadata was not found.')

        # log extracted metadata 
        logging.info(f"Metadata in {video_path}: {metadata_embedded}")

# References:
# https://ffmpeg.org/ffmpeg.html
# https://docs.python.org/3/library/subprocess.html
# https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
# https://www.warp.dev/terminus/python-delete-file
# https://ffmpeg.org/ffprobe.html
# https://superuser.com/questions/891665/ffprobe-show-entries-with-an-entry-name-that-uses-a-semicolon
# https://github.com/aclap-dev/vdhcoapp/issues/9
# https://www.bogotobogo.com/python/python-json-dumps-loads-file-read-write.php

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """