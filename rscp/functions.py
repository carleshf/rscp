###############################################################################
# RSCP // FUNCTIONS                                                           #
# by Carles Hernandez-Ferrer                                                  #
# and In-Hee Lee                                                              #
# (C) Boston Children's Hospital                                              #
#     McLean Hospital                                                         #
###############################################################################


# IMPORTS
###############################################################################
import random
import string
import datetime
import smtplib
import ssl
from os import environ as env

from sys import stderr as err
from messages import email_grant_access


# FUNCTIONS
###############################################################################

# Add a string (comment) to apache2 error log
def write_log(txt):
    err.write('[FOLDER LOG]: %s\n' % str(txt))
    err.flush()

def today():
	return datetime.datetime.now()

# Create a random string
def generate_random_string():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(10)])

# Create tag for file
def generate_tag(user_id):
    now = datetime.datetime.now()
    return 'x.' + str(user_id) + '.' + str(now.year) + '.' + generate_random_string() + '.' + str(now.month) + '.' + str(now.day)

# Function to send email
def send_email_grant_access(receiver, url_token, server = 'smtp.gmail.com', port = 465):
    try:
        content = email_grant_access(url_token)
        server = smtplib.SMTP_SSL(env['EMAIL_SERVER'], int(env['EMAIL_PORT']))
        server.login(env['EMAIL_USER'], env['EMAIL_PASSWORD'])
        server.sendmail(env['EMAIL_USER'], receiver, content)
        return True
    except Exception, ex:
        write_log('Error on sending email to "' + str(receiver) + '".')
        return False
