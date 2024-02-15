from app import db
from flask_login import current_user
import logging
from app.database_models.models import MotionEvent, Position, MotionSize, DetectedObject, ObjectType

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

logging.basicConfig(level=logging.INFO)

def save_motion_event_to_database(video_path, image_path, position_name, size_name, detected_objects, user_id=None):
    try:
        # log to show whats being saved 
        logging.debug(f"Saving event to db: video_path={video_path}, image_path={image_path}, position_name={position_name}, size_name={size_name}, user_id={user_id}")
        
        # get Position and MotionSize objects from db
        position = Position.query.filter_by(name=position_name).first()
        motion_size = MotionSize.query.filter_by(size_name=size_name).first()

        if not position or not motion_size:
            logging.error("Position or MotionSize were not found in db.")
            return None

        # create new MotionEvent instance with data
        event = MotionEvent(
            video_path=video_path,
            image_path=image_path,
            position=position,
            motion_size=motion_size,
            user_id=user_id if user_id else getattr(current_user, 'user_id', None)
        )

        # adds MotionEvent instance to db session 
        db.session.add(event)
        # flush to get event_id
        db.session.flush()

        # create a set to track unique detected objects based on class_name
        detected_objects_unique_set = set()

        # loops detected_objects and creates DetectedObject instances
        for object in detected_objects:
            # to avoid duplicates checks if object with same class_name has already been added 
            if object['class_name'] not in detected_objects_unique_set:
                detected_obj = DetectedObject(
                    motion_event_id=event.event_id,
                    class_name=object['class_name'],
                    score=object['score']
                )
                
                # gets object_type_id based on the class_name
                object_type_name = object['object_type']
                object_type = ObjectType.query.filter_by(name=object_type_name).first()

                if object_type:
                    detected_obj.object_type_id = object_type.object_type_id
                else:
                    logging.warning(f"Object type '{object_type_name}' was not found in db. Default value will be used.")

                # adds DetectedObject instance to db session
                db.session.add(detected_obj)

                # adds class_name to set of unique detected objects
                detected_objects_unique_set.add(object['class_name'])

        # commit changes to db
        db.session.commit()
        
        # logs detected objects (decided to keep as it's very useful)
        for object in detected_objects:
            logging.info(f"Detected object saved for event id {event.event_id}: "
                         f"Class Name: {object['class_name']}, "
                         f"Detection Score: {object['score']}, "
                         f"Object Type: {object['object_type']}")

        logging.info(f"Motion event was saved with event_id: {event.event_id}")
        return event.event_id

    except Exception as e:
        logging.error(f"Error saving event: {e}", exc_info=True)
        return None

# References:
# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://www.python-forum.de/viewtopic.php?t=51700
# https://www.pythonanywhere.com/forums/topic/28656/
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
# https://www.digitalocean.com/community/tutorials/how-to-query-tables-and-paginate-data-in-flask-sqlalchemy
# https://docs.python.org/3/howto/logging.html
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html
# https://stackoverflow.com/questions/38506216/flask-mysql-db-session-add-error
# https://docs.sqlalchemy.org/en/20/orm/session_api.html
# https://stackoverflow.com/questions/4201455/sqlalchemy-whats-the-difference-between-flush-and-commit
# https://michaelcho.me/article/sqlalchemy-commit-flush-expire-refresh-merge-whats-the-difference/
# https://invenio-talk.web.cern.ch/t/understanding-database-session-management-and-transactions-in-invenio/33

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """