activate_this='path_to_virtualenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys, os

os.environ['APP_HOME'] = 'path_to_app'
os.environ['DDBB_USER'] = 'ddbb_user'
os.environ['DDBB_HOST'] = 'ddbb_server'
os.environ['DDBB_NAME'] = 'ddbb_database_name'
os.environ['DDBB_PASSWORD'] = 'ddbb_password'
os.environ['DDBB_PORT'] = 'ddbb_port'
os.environ['APP_SECRET'] = 'app_secret'
os.environ['EMAIL_USER'] = 'email_user'
os.environ['EMAIL_PASSWORD'] = 'email_password'
os.environ['EMAIL_SERVER'] = 'email_server'
os.environ['EMAIL_PORT'] = 'email_port'
os.environ['EMAIL_FLAG'] = 'False' # Set to true to use email

sys.path.insert(0, 'path_to_app')
from app import app as application
