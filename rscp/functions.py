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
import csv
from os import environ as env

from sys import stderr as err
from messages import email_grant_access, invalid_data, invalid_col_num
from messages import invalid_sex, invalid_strain, invalid_datatype

import database as db


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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in env['APP_ALLOWED_EXTENSIONS']

# Load data
def read_table_files(file_path):
    """The expected columns of the file must be in this order:
        0. subject          1. sex (male/female)
        2. strain           2. cline
        4. method           5. datatype
        6. datafile_path    7. datafile_name
        8. datafile_passage 9. datafile_instrument
    """
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        error = 0
        data = []
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                if len(row) != 10:
                    return {'error': invalid_col_num(), 'data': []}
                line_count += 1
            else:
                row.append('')
                x = len(row) - 1
                if not db.check_sex(row[1]):
                    row[x] += invalid_sex()
                    error += 1
                if not db.check_strain(row[2]):
                    row[x] += invalid_strain()
                    error += 1
                if not db.check_datatype(row[5]):
                    row[x] += invalid_datatype()
                    error += 1
                data.append(row)
        if error == 0:
            return {'error': error, 'data': data}
        else:
            return {'error': error, 'data': data}


