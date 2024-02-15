from app.__init__ import db
from app.database_models.models import Role

""" START - This code was copied from refereced resources. Please see referenced links. 
"""

# sets up predefined roles in db (this needs to be commented out if setting up new db, otherwise, it will rasie an error)
def setup_roles(app):
    with app.app_context():
        roles = ['admin', 'user']
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
        db.session.commit()
        
# References:
# https://flask-user.readthedocs.io/en/latest/authorization.html
# https://flask.palletsprojects.com/en/2.3.x/appcontext/
# https://laracasts.com/discuss/channels/general-discussion/users-roles-and-filters
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html

""" END - This code was copied from refereced resources. Please see referenced links. 
"""