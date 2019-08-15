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

class Request(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	idUser = db.Column(db.Integer)
	tag = db.Column(db.String(25))
	validated = db.Column(db.Boolean())
	registered = db.Column(db.Boolean())
	request_date = db.Column(db.DateTime)
	validated_date = db.Column(db.DateTime)
	registered_date = db.Column(db.DateTime)

	def __str__(self):
		return'[REQUEST]: for user id ' + str(self.idUser) + ' (id: ' + str(self.id) + '; on: ' + str(self.request_date) + ')'


class Datatype(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	description = db.Column(db.String(300))

class Method(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	description = db.Column(db.String(300))

	def __str__(self):
		return'[METHOD]: ' + str(self.description) + ' (id: ' + str(self.id) + ')'

class Strain(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	description = db.Column(db.String(300))

class Subject(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	idStrain = db.Column(db.Integer)
	description = db.Column(db.String(300))
	sex = db.Column(db.String(25))
	age = db.Column(db.Integer)

	def __str__(self):
		return'[SUBJECT]: ' + self.description + ' (id: ' + str(self.id) + '; strain id: ' + str(self.idStrain) + ')'

class Cline(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	idMethod = db.Column(db.Integer)
	idSubject = db.Column(db.Integer)
	description = db.Column(db.String(300))
	bank_status = db.Column(db.String(300))
	growing = db.Column(db.String(300))

	def __str__(self):
		return'[LINE]: ' + str(self.description) + ' (id: ' + str(self.id) + ')'

class Datafile(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	idLine = db.Column(db.Integer)
	idType = db.Column(db.Integer)
	filepath = db.Column(db.String(5000))
	displayname = db.Column(db.String(500))
	passage = db.Column(db.Integer)
	instrument = db.Column(db.String(500))

# FUNCTIONS FOR USERS
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


# FUNCTIONS FOR DATA MATRIX
###############################################################################

def get_sex():
	query = db.engine.execute("""SELECT subject.sex, COUNT(subject.sex) FROM subject, strain, method, cline, datafile, datatype WHERE
	    subject.idStrain = strain.id AND 
	    cline.idMethod = method.id AND
	    cline.idSubject = subject.id AND
	    datafile.idLine = cline.id AND
	    datafile.idType = datatype.id
	    GROUP BY subject.sex;""")
	return query

def get_line():
	query = db.engine.execute("""SELECT cline.description, COUNT(cline.description) FROM subject, strain, method, cline, datafile, datatype WHERE
	    subject.idStrain = strain.id AND 
	    cline.idMethod = method.id AND
	    cline.idSubject = subject.id AND
	    datafile.idLine = cline.id AND
	    datafile.idType = datatype.id
	    GROUP BY cline.description;""")
	return query

def get_method():
	query = db.engine.execute("""SELECT method.description, COUNT(method.description) FROM subject, strain, method, cline, datafile, datatype WHERE
	    subject.idStrain = strain.id AND 
	    cline.idMethod = method.id AND
	    cline.idSubject = subject.id AND
	    datafile.idLine = cline.id AND
	    datafile.idType = datatype.id
	    GROUP BY method.description;""")
	return query

def get_strain(count=True):
	if count:
		query = db.engine.execute("""SELECT strain.description, COUNT(strain.description) FROM subject, strain, method, cline, datafile, datatype WHERE
		    subject.idStrain = strain.id AND 
		    cline.idMethod = method.id AND
		    cline.idSubject = subject.id AND
		    datafile.idLine = cline.id AND
		    datafile.idType = datatype.id
		    GROUP BY strain.description;""")
	else:
		query = db.session.query(Strain.description) \
			.distinct()
	return query

def get_datatype(count=True):
	if count:
		query = db.engine.execute("""SELECT datatype.description, COUNT(datatype.description) FROM subject, strain, method, cline, datafile, datatype WHERE
		    subject.idStrain = strain.id AND 
		    cline.idMethod = method.id AND
		    cline.idSubject = subject.id AND
		    datafile.idLine = cline.id AND
		    datafile.idType = datatype.id
		    GROUP BY datatype.description;""")
	else:
		query = db.session.query(Datatype.description) \
			.distinct()
	return query

def check_sex(value):
	value = value.lower()
	return value in ['male', 'female']

def check_strain(value):
	x = get_strain(False)
	return value in [y[0] for y in x]

def check_datatype(value):
	x = get_datatype(False)
	return value in [y[0] for y in x]

def db_get_strain_id(value):
	query = db.session.query(Strain.id) \
		.filter(Strain.description == value) \
		.first()
	return query[0]

def db_get_datatyle_id(value):
	query = db.session.query(Datatype.id) \
		.filter(Datatype.description == value) \
		.first()
	return query[0]

def db_get_subject_id(value):
	query = db.session.query(Subject.id) \
		.filter(Subject.description == value) \
		.first()
	if query:
		return query[0]
	else:
		return -1

def db_get_cline(value, idMethod, idSubject):
	query = db.session.query(Cline.id) \
		.filter(Cline.description == value and Cline.idSubject == idSubject and Cline.idMethod == idMethod) \
		.first()
	if query:
		return query[0] 
	else:
		return -1

def db_get_method(value):
	query = db.session.query(Method.id) \
		.filter(Method.description == value) \
		.first()
	if query:
		return query[0]
	else:
		return -1

def db_get_datatype(value):
	query = db.session.query(Datatype.id) \
		.filter(Datatype.description == value) \
		.first()
	if query:
		return query[0]
	else:
		return -1

def insert_data(table):
	try:
		for row in table:
			# check if method is already in database
			idMethod = db_get_method(row[4])
			if idMethod == -1:
				new_method = Method(description = row[4])
				db.session.add(new_method)
				fun.write_log(str(new_method))
				db.session.flush()
				idMethod = new_method.id

			# check if subject is already in the database
			idSubject = db_get_subject_id(row[0])
			if idSubject == -1:
				idStrain = db_get_strain_id(row[2])
				new_subject = Subject(idStrain = idStrain, description = row[0], sex = row[1].lower(), age = -1)
				db.session.add(new_subject)
				fun.write_log(str(new_subject))
				db.session.flush()
				idSubject = new_subject.id
				
				new_cline = Cline(idSubject = idSubject, idMethod = idMethod, description = row[3], bank_status = '', growing = '')
				db.session.add(new_cline)
				fun.write_log(str(new_cline))
				db.session.flush()
				idLine = new_cline.id
			else:
				idLine = db_get_cline(row[3], idMethod, idSubject)
				if idLine == -1:
					new_cline = Cline(idSubject = idSubject, idMethod = idMethod, description = row[3], bank_status = '', growing = '')
					db.session.add(new_cline)
					fun.write_log(str(new_cline))
					db.session.flush()
					idLine = new_cline.id

			idType = db_get_datatype(row[5])
			if idType == -1:
				new_data_type = Datatype(description = row[5])
				db.session.add(new_datatype)
				idType = new_data_type.id

			try:
				passage = int(row[8])
			except:
				passage = -1

			new_data_file = Datafile(idLine = idLine, idType = idType, filepath = row[6], displayname = row[7], passage = passage, instrument = row[9])
			db.session.add(new_data_file)

			db.session.commit()
	except:
		return False
	return True


def get_table():
	query = db.engine.execute("""SELECT * FROM subject, strain, method, cline, datafile, datatype WHERE
		    subject.idStrain = strain.id AND 
		    cline.idMethod = method.id AND
		    cline.idSubject = subject.id AND
		    datafile.idLine = cline.id AND
		    datafile.idType = datatype.id;""")
	return query
