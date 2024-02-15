from app import db, create_app  

""" START - This code was copied from refereced resources. Please see referenced links. 
"""

def init_db():
    with create_app().app_context():
        db.create_all()

if __name__ == "__main__":
    init_db()

# References:
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/contexts/
# https://flask.palletsprojects.com/en/3.0.x/tutorial/database/#
# https://xvrdm.github.io/2017/07/03/testing-flask-sqlalchemy-database-with-pytest/
# https://flask.palletsprojects.com/en/2.3.x/cli/
# https://github.com/lingthio/Flask-User-starter-app/blob/master/app/commands/init_db.py
# https://www.pythonanywhere.com/forums/topic/28656/
# https://flask.palletsprojects.com/en/2.3.x/cli/
# https://stackoverflow.com/questions/6244382/how-to-automate-createsuperuser-on-django
# https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/cli.py
# https://www.forestadmin.com/blog/flask-tastic-admin-panel-a-step-by-step-guide-to-building-your-own-2/
# https://stackoverflow.com/questions/62096867/first-time-creating-a-website-with-flask-i-keep-coming-up-with-error-no-such
# https://www.linkedin.com/pulse/creating-custom-cli-commands-flask-skill-gain
# https://github.com/miguelgrinberg/Flask-Migrate/issues/210
# https://www.reddit.com/r/flask/comments/ykm1w4/dbcreate_all_not_working/
# https://stackoverflow.com/questions/50963130/how-to-run-invoke-a-flask-cli-command-programmatically

""" END - This code was copied from refereced resources. Please see referenced links. 
"""