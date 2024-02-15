from app.database_models.models import  MotionEvent
import logging


""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

def retrieve_video_file_path(event_id):
    # checks if event_id is None
    if event_id is None:
        logging.error("Received None for event_id in retrieve_video_file_path")
        return None

    # query db
    event = MotionEvent.query.get(event_id)
    
    # if event is found, get the video file path
    if event:
        video_path = event.video_path
        logging.info(f"Video file path for event {event_id}: {video_path}")
        return video_path
    else:
        # otherwise log error
        logging.error(f"Video file not found for event {event_id}")
        return None

# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://stackoverflow.com/questions/34299704/when-to-use-sqlalchemy-get-vs-filterfoo-id-primary-key-id-first
# https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
# https://www.freecodecamp.org/news/how-to-read-and-write-data-to-a-sql-database-using-python/


""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """