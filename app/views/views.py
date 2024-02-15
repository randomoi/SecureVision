from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request
from flask_admin.form import rules
from flask_admin import AdminIndexView
from app.forms.forms_custom_user import UserCustomForm
from app.views.formatters_utilities import events_formatter, roles_formatter

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

class UserModelView(ModelView):
    form = UserCustomForm
    
    # sets permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to be displayed 
    column_list = ('user_id', 'email', 'first_name', 'last_name', 'roles', 'events', 'google_drive_enabled', 'email_notification_preference', 'motion_detection_mode')
    
    # enables searching 
    column_searchable_list = ('user_id', 'email', 'first_name', 'last_name')
    
    # excludes password_hash column 
    column_exclude_list = ['password_hash']
    
    # excludes password_hash column from form
    form_excluded_columns = ['password_hash']

    # format columns 
    column_formatters = {
        'roles': roles_formatter,
        'events': events_formatter
    }
    
    # rules 
    form_rules = [
        rules.FieldSet(('first_name', 'last_name', 'email', 'roles', 'events', 'google_drive_enabled', 'email_notification_preference', 'motion_detection_mode'), 'Personal Info'),
    ]

    # excludes password_hash column 
    column_details_exclude_list = ['password_hash']

    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
    
    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))

    
class RoleModelView(ModelView):
    # sets permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to be displayed 
    column_list = ('role_id', 'name')
    
    # enables searching 
    column_searchable_list = ('name',)

    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
    
    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))

class MotionEventModelView(ModelView):
    # custom column formatter 
    def detected_objects_formatter(view, context, model, name):
        if model.detected_objects:
            return ", ".join([f"{obj.class_name} (Score: {obj.score:.2f})" for obj in model.detected_objects])
        return "No objects were detected."
    
    # sets permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to display 
    column_list = ('event_id', 'timestamp', 'position', 'motion_size', 'detected_objects', 'video_path', 'image_path', 'user', 'google_drive_file_id')
    
    # custom column formatter
    column_formatters = {
        'roles': roles_formatter,
        'events': events_formatter,
        'detected_objects': detected_objects_formatter
    }

    # defines searchable columns
    column_searchable_list = ('event_id', 'video_path', 'image_path')

    # sets number of items per page 
    page_size = 900 

    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
    
    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))

class ObjectTypeModelView(ModelView):
    # sets permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to display 
    column_list = ('object_type_id', 'name')
    
    # define searchable column
    column_searchable_list = ('name',)

    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))


class DetectedObjectModelView(ModelView):
    # custom formatter 
    def object_type_formatter(self, context, model, name):
        if model.object_type:
            return model.object_type.name  
        else:
            return "Unknown"

    # set permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to display
    column_list = ('detected_object_id', 'class_name', 'score', 'object_type')
    
    # searchable column
    column_searchable_list = ('class_name',)

    # uses custom method 
    column_formatters = {
        'object_type': object_type_formatter
    }
    
    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))

 
class MotionSizeModelView(ModelView):
    # sets permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to display 
    column_list = ('size_id', 'size_name', 'events')
    
    # searchable column
    column_searchable_list = ('size_name',)

    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')

    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))


class MotionPositionModelView(ModelView):
    # set permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to display 
    column_list = ('position_id', 'name')
    
    # searchble column
    column_searchable_list = ('name',)
    
    # columns can be sorted
    column_sortable_list = ('position_id', 'name')

     # check if user is authenticatedw
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
    
    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))


class TokenModelView(ModelView):
    # set permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    #columns to display 
    column_list = ('token_id', 'access_token', 'refresh_token', 'expires_at', 'token_type')
    
    # searchable columns
    column_searchable_list = ('token_id', 'access_token')
    
    # excludes from form
    form_excluded_columns = ['access_token', 'refresh_token'] 

     # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
    
     # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))

class GoogleDriveTokenModelView(ModelView):
    # sets permissions for CRUD ops
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    # columns to display 
    column_list = ('google_drive_token_id', 'access_token', 'refresh_token', 'expires_at', 'user_id')
    
    # searchnable columns
    column_searchable_list = ('google_drive_token_id', 'access_token')
    
    # excludes from form
    form_excluded_columns = ['access_token', 'refresh_token'] 

    # check if user is authenticated
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('admin')
    
    # redirects to login page if user is not authorized
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('blueprint_user_authentication.login', next=request.url))



# hides Flask-Admin default EMPTY homepage
# https://flask-admin.readthedocs.io/en/latest/api/mod_base/
class MyAdminIndexView(AdminIndexView):
    def is_visible(self):
        return False

# References:
# https://flask-admin.readthedocs.io/en/latest/
# https://flask-admin.readthedocs.io/en/latest/api/mod_base/
# https://flask-admin.readthedocs.io/en/latest/api/mod_model/
# https://stackoverflow.com/questions/33646165/flask-admin-is-accessible-usage
# https://github.com/flask-admin/flask-admin/issues/1104
# https://ryansblog2718281.medium.com/flask-login-and-is-authenticated-94bdb0aecd46
# https://flask-login.readthedocs.io/en/latest/
# https://flask-security-too.readthedocs.io/en/stable/api.html
# https://dev.to/abbazs/flask-user-currentuser-hasroles-admin-185j
# https://stackoverflow.com/questions/61624338/flask-admin-remove-home-button
# https://flask-admin.readthedocs.io/en/latest/api/mod_model/
# https://flask-admin.readthedocs.io/en/latest/api/mod_form/
# https://flask-admin.readthedocs.io/en/latest/api/mod_form_rules/
# https://flask-admin.readthedocs.io/en/latest/api/mod_form_fields/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""