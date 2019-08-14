###############################################################################
# RSCP // DATABASE                                                            #
# by Carles Hernandez-Ferrer                                                  #
# and In-Hee Lee                                                              #
# (C) Boston Children's Hospital                                              #
#     McLean Hospital                                                         #
###############################################################################

# IMPORTS
###############################################################################
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

import functions as fun

# DATABASE
###############################################################################

# Initialization of SQLAlchemy so we can use it our models
db = SQLAlchemy()

# DDBB models: user
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(150))
	surname = db.Column(db.String(300))
	institution = db.Column(db.String(500))
	email = db.Column(db.String(500))
	password = db.Column(db.String(50))
	type = db.Column(db.String(25))

	def __str__(self):
		return'[USER]: ' + self.name + '(id: ' + str(self.id) + ')'

class Request (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	idUser = db.Column(db.Integer)
	tag = db.Column(db.String(25))
	validated = db.Column(db.Boolean())
	registered = db.Column(db.Boolean())
	request_date = db.Column(db.DateTime)
	validated_date = db.Column(db.DateTime)
	registered_date = db.Column(db.DateTime)

	def __str__(self):
		return'[REQUEST]: for user id ' + str(self.idUser) + '(id: ' + str(self.id) + '; on: ' + str(self.request_date) + ')'


# FUNCTIONS
###############################################################################
def email_exists(email):
	user = User.query.filter_by(email = email).count()
	return user != 0

def sign_up_user(name, surname, email, institution):
	process_ended_ok = False
	try:
		new_user = User(name = name, surname = surname, institution = institution, \
		email = email, type = 'User')
		db.session.add(new_user)
		db.session.flush()

		fun.write_log(str(new_user))

		new_request = Request(idUser = new_user.id, tag = fun.generate_tag(new_user.id), \
		validated = False, registered = False, request_date = fun.today(),
		validated_date = None, registered_date = None)

		db.session.add(new_request)
		db.session.flush()

		fun.write_log(str(new_request))
		db.session.commit()
		process_ended_ok = True
	except Exception, ex:
		db.session.rollback()
		fun.write_log('Error occurred while inserting new user and its request: ' + str(ex.message))
	return process_ended_ok

def autenticate_user(email, password):
	type_of_user = 'User'
	user = User.query.filter_by(email=email).first()
	if not user or not user.password == password:
		type_of_user = '*error*'
		fun.write_log('Failed attempt to validate "' + str(email) + '"')
	else:
		type_of_user = user.type
	
	return (type_of_user, user)


def list_pending_requests():
	peding_requests = db.session.query(User, Request) \
		.filter(Request.idUser == User.id) \
		.filter(Request.validated == False or Request.registered == False)
	return peding_requests


def list_validated_users():
	users = db.session.query(User, Request) \
		.filter(Request.idUser == User.id) \
		.filter(Request.validated == True and Request.registered == True)
	return users


def get_data_grant_access(idRequest):
	request = db.session.query(User, Request) \
		.filter(Request.idUser == User.id) \
		.filter(Request.id == idRequest) \
		.first()
	if request:
		return request
	else:
		return None


def generate_token_grant_access(idRequest):
	try:
		reqst = db.session.query(Request) \
			.filter(Request.id == idRequest) \
			.first()
		reqst.tag = fun.generate_tag(reqst.idUser)
		db.session.commit()
		return True
	except Exception, ex:
		fun.write_log('Error during generating new token for validation of request "' + str(idRequest) + '".')
		db.session.rollback()
		return False

def get_user_by_token(token):
	user = db.session.query(User, Request) \
		.filter(Request.idUser == User.id) \
		.filter(Request.tag == token) \
		.first()
	if user:
		return user
	else:
		return None

def update_password(idUser, password):
	try:
		user = db.session.query(User) \
			.filter(User.id == idUser) \
			.first()
		user.password = password
		db.session.commit()
		return True
	except Exception, ex:
		fun.write_log('Error during updating password for "' + str(idUser) + '".')
		db.session.rollback()
		return False

