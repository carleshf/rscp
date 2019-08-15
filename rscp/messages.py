###############################################################################
# RSCP // MESSAGES                                                            #
# by Carles Hernandez-Ferrer                                                  #
# and In-Hee Lee                                                              #
# (C) Boston Children's Hospital                                              #
#     McLean Hospital                                                         #
###############################################################################

from string import Template

# -- SIGN UP -------------------------------------------------------------------
def signup_email_diff():
	return 'Provided email and confirmation do not match.'

def signup_email_empty():
	return 'Provided email cannot be empty.'

def signup_other_empty():
	return 'Name, surname, and institution cannot be empty.'

def signup_email_exists():
	return 'Provided email is already in use.'

def signup_reuest_sucess():
	return 'We collected your information. One of our administrators ' + \
		'will validate your request as soon as possible and contact you ' + \
		'with the next step.'

def signup_reuest_error():
	return 'We detected a problem processing your request. Please, contact ' + \
		'our staff to solved this issue.'

# -- LOGIN --------------------------------------------------------------------
def login_invalid():
	return 'Please check your login details and try again.'

# -- PROFILE ------------------------------------------------------------------

def update_password_wrong():
	return 'Your password and confirmation password do not match.'

def update_password_empty():
	return 'Your cannot be empty.'

def update_password_unknown():
	return 'An unknown error raised during the update of your password. ' + \
		'Please, contact with our staff to solve this issue.'

def update_password_success():
	return 'Your password was updated.'

# -- ADMIN - GRANT ACCESS -----------------------------------------------------
def grant_access_request_error():
	return 'An error occurred and no request could be located. Please, check ' + \
		'with the database administrator the origin of this issue.'

def grant_access_email_error(request):
	return 'We could not send the e-mail to "' + str(request.User.email) + '".'

def grant_acces_email_sucess(request):
	return 'The e-mail to "' + str(request.User.email) + '" was successfully sent.'

def email_grant_access(url_token):
	content = """\
Subject: Access to rSCP

This message is to confirm the creation of a new account into the rSCP's server.

Please, follow the next link to activate your account and set-up a password:

https://tom.tch.harvard.edu${URL}
 

Bests,
The rSCP staff
"""
	return Template(content).substitute(URL=url_token)

# -- ADMIN - LOAD DATA -----------------------------------------------------

def upload_file_emtpy_wrong():
	return 'Please, provide a CSV file with the information to insert ' + \
		'into the database.'

def invalid_col_num():
	return 'Incorrect number of columns.'

def invalid_sex():
	return 'Invalid value for "sex".'

def invalid_strain():
	return 'Invalid value for "strain".'

def invalid_datatype():
	return 'Invalid value for "datatype".'

def invalid_data():
	return 'Data provided contains invalid values.'