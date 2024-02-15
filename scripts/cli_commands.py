import click
from flask.cli import with_appcontext
from app.database_models.models import db, Role, User, ObjectType
from app.email_notifications.gmail_token_services import save_gmail_api_tokens_in_database

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

@click.command('init-default-roles')
@with_appcontext
def init_default_roles_command():
    roles = ['admin', 'user']

    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name)
            db.session.add(role)

    db.session.commit()
    click.echo('Default roles were initialized.')

@click.command('create-superuser')
@with_appcontext
def create_superuser():
    first_name = click.prompt('First Name')  
    last_name = click.prompt('Last Name')   
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True)
    user = User(first_name=first_name, last_name=last_name, email=email)  
    user.set_password(password)

    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        user.roles.append(admin_role)

    db.session.add(user)
    db.session.commit()
    click.echo("Created Superuser!!")

@click.command('make-admin-user')
@with_appcontext
def make_admin_user_command():
    email = click.prompt('Email of user to make admin')
    
    user = User.query.filter_by(email=email).first()
    if user:
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            user.roles.append(admin_role)
            db.session.commit()
            click.echo(f'{user.email} is now an admin.')
        else:
            click.echo('Admin role not found.')
    else:
        click.echo(f'User with email {email} was not found.')
        
@click.command('init-database')
@with_appcontext
def init_database_command():
    db.create_all()
    click.echo('Initialized db.')

from app.database_models.models import Position, MotionSize

@click.command('init-default-position-size')
@with_appcontext
def init_default_position_size_command():
    positions = ['Left', 'Right']
    for position_name in positions:
        position = Position.query.filter_by(name=position_name).first()
        if not position:
            position = Position(name=position_name)
            db.session.add(position)

    sizes = ['Small', 'Large']
    for size_name in sizes:
        motion_size = MotionSize.query.filter_by(size_name=size_name).first()
        if not motion_size:
            motion_size = MotionSize(size_name=size_name)
            db.session.add(motion_size)

    db.session.commit()
    click.echo('Default data for Position and MotionSize were created.')

@click.command('init-default-object-types')
@with_appcontext
def init_default_object_types_command():
    object_types = ['Human', 'Animal']
    
    for object_type_name in object_types:
        object_type = ObjectType.query.filter_by(name=object_type_name).first()
        if not object_type:
            object_type = ObjectType(name=object_type_name)
            db.session.add(object_type)

    db.session.commit()
    click.echo('Default detected object types were created.')
    
@click.command('init-gmail-tokens')
@with_appcontext
def init_gmail_tokens_command():
    access_token = click.prompt('Access Token')  
    refresh_token = click.prompt('Refresh Token')  
    expires_in = click.prompt('Expires In', type=int)  
    
    save_gmail_api_tokens_in_database(access_token, refresh_token, expires_in)
    click.echo('Gmail API tokens were stored.')

def register_commands(app):
    app.cli.add_command(init_default_roles_command)
    app.cli.add_command(create_superuser)
    app.cli.add_command(init_database_command) 
    app.cli.add_command(init_default_position_size_command)  
    app.cli.add_command(make_admin_user_command)
    app.cli.add_command(init_gmail_tokens_command)
    app.cli.add_command(init_default_object_types_command)  
    
# References:   
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
# https://click.palletsprojects.com/en/8.1.x/prompts/
# https://click.palletsprojects.com/en/8.1.x/api/#click.echo
# https://hackersandslackers.com/flask-login-user-authentication/
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""