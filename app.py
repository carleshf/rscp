###############################################################################
# RSCP                                                                        #
# by Carles Hernandez-Ferrer                                                  #
# and In-Hee Lee                                                              #
# (C) Boston Children's Hospital                                              #
#     McLean Hospital                                                         #
###############################################################################

from os import environ as env
from os import path
from flask import Flask, Blueprint, render_template, redirect, url_for
from flask import request, flash, send_file
from flask_login import LoginManager, login_user, login_required
from flask_login import logout_user, current_user
from werkzeug.utils import secure_filename

from rscp.database import db, email_exists, sign_up_user, autenticate_user
from rscp.database import list_pending_requests, list_validated_users
from rscp.database import get_data_grant_access, generate_token_grant_access
from rscp.database import get_user_by_token, update_password, insert_data
from rscp.database import get_strain, get_sex, get_datatype, get_table
from rscp.database import get_method, get_line
from rscp import functions as fun
import rscp.messages as msg
from rscp.database import User

# AUTHENTICATION APPLICATION ENDPOINTS
###############################################################################
# They include:
#    - /login
#    - /logout
#    - /signup

auth = Blueprint('auth', __name__)

# -- LOGIN --------------------------------------------------------------------
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email').strip()
	password = request.form.get('password')
	type_of_user = autenticate_user(email, password)
	if type_of_user[0] == '*error*':
		flash(msg.login_invalid())
		return redirect(url_for('auth.login'))
	elif type_of_user[0] == 'Administrator':
		login_user(type_of_user[1], remember = False)
		return redirect(url_for('main.admin'))
	elif type_of_user[0] == 'User':
		login_user(type_of_user[1], remember = False)
		return redirect(url_for('main.profile'))
	else:
		return redirect(url_for('main.home'))

# -- LOGOUT -------------------------------------------------------------------
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))

# -- SIGN UP -------------------------------------------------------------------
@auth.route('/signup')
def signup():
	return render_template('signup.html')

@auth.route('/signup', methods = ['POST'])
def signup_post():
	name = request.form.get('name').strip()
	surname = request.form.get('surname').strip()
	institution = request.form.get('institution').strip()
	email1 = request.form.get('email').strip()
	email2 = request.form.get('email_conf').strip()
	valid = False
	if email1 != email2:
		flash(msg.signup_email_diff(), 'error')
	elif email1 == '' or email2 == '':
		flash(msg.signup_email_empty(), 'error')
	elif name == '' or surname == '' or institution == '':
		flash(msg.signup_other_empty(), 'error')
	elif email_exists(email1):
		flash(msg.signup_email_exists(), 'error')
	else:
		insertion_ok = sign_up_user(name, surname, email1, institution)
		if insertion_ok:
			flash(msg.signup_reuest_sucess(), 'info')
		else:
			flash(msg.signup_reuest_error(), 'error')
	return redirect(url_for('auth.signup'))

# MAIN APPLICATION ENDPOINTS
###############################################################################
# They include:
#    - / and /home: to show the main page (index.html)

main = Blueprint('main', __name__)

# -- INDEX ------------------------------------------------------------------
@main.route('/')
def index():
	return render_template('index.html')

@main.route('/home')
def home():
	return render_template('index.html')

# -- ACCOUNT ------------------------------------------------------------------
@main.route('/profile')
@login_required
def profile():
	return render_template('profile.html', name = current_user.name, \
		surname = current_user.surname, email = current_user.email, \
		institution = current_user.institution)

@main.route('/profile', methods = ['POST'])
@login_required
def profile_post():
	password1 = request.form.get('password1')
	password2 = request.form.get('password2')
	if password1 != password2:
		flash(msg.update_password_wrong(), 'error')
	elif password1 == '' or password2 == '':
		flash(msg.update_password_empty(), 'error')
	elif update_password(idUser, password1):
		flash(msg.update_password_success(), 'info')
	else:
		flash(msg.update_password_unknown(), 'error')
	return redirect(url_for('main.profile'))


# -- ADMIN - MENU -------------------------------------------------------------
@main.route('/admin')
@login_required
def admin():
	return render_template('admin.html')

# -- ADMIN - LIST OF REQUESTS -------------------------------------------------
@main.route('/request_manager')
def request_manager():
	requests = list_pending_requests()
	return render_template('requests_manager.html', pending_requests = requests)

# -- ADMIN - LIST OF USERS -----------------------------------------------------
@main.route('/user_manager')
def user_manager():
	users = list_validated_users()
	return render_template('users_manager.html', users = users)

# -- ADMIN - GRANT ACCESS -----------------------------------------------------
@main.route('/grant_access', methods = ['GET'])
def grant_access_get():
	idRequest = request.args.get('reqid')
	generate_token_grant_access(idRequest)
	reqs = get_data_grant_access(idRequest)
	if not reqs is None:
		url_token = url_for('main.xyz', token = reqs.Request.tag)
		if fun.send_email_grant_access(reqs.User.email, url_token):
			reqs.Request.validated_date = fun.today()
			db.session.commit()
			flash(msg.grant_acces_email_sucess(reqs), 'info')
		else:
			flash(msg.grant_access_email_error(reqs), 'error')
	else:
		flash(msg.grant_access_request_error(), 'error')
	return redirect(url_for('main.request_manager'))

@main.route('/xyz', methods = ['GET'])
def xyz():
	token = request.args.get('token')
	user = get_user_by_token(token)
	return render_template('activate_account.html', email = user.User.email, token = token)

@main.route('/xyz', methods = ['POST'])
def xyz_post():
	token = request.form.get('token').strip()
	user = get_user_by_token(token)
	password1 = request.form.get('password1')
	password2 = request.form.get('password2')
	show_login = False
	if password1 != password2:
		flash(msg.update_password_wrong(), 'error')
	elif password1 == '' or password2 == '':
		flash(msg.update_password_empty(), 'error')
	elif update_password(user.User.id, password1):
		show_login = True
	else:
		flash(msg.update_password_unknown(), 'error')
	if show_login:
		return redirect(url_for('auth.login'))
	else:	
		return redirect(url_for('main.xyz', token = token))

# -- ADMIN - UPLOAD LIST OF FILES -----------------------------------------------------
@main.route('/add_file')
@login_required
def add_file():
	if current_user.type == 'Administrator':
		stage = request.args.get('stage')
		data = request.args.get('data')
		if not stage:
			stage = 'stage1'
		if not data:
			data = []
		return render_template('add_file.html', stage = stage, data = data)
	else:
		redirect(url_for('main.profile'))

@main.route('/add_file', methods = ['GET', 'POST'])
@login_required
def add_file_post():
	if current_user.type == 'Administrator':
		stage = 'stage1'
		data = []
		if request.method == 'POST':
			file = request.files['file']
			if not file:
				flash(msg.upload_file_emtpy_wrong(), 'error')
			if file.filename == '':
				flash(msg.upload_file_emtpy_wrong(), 'error')
			if file and fun.allowed_file(file.filename):
				filename = secure_filename(file.filename)
				filepath = path.join(app.config['UPLOAD_FOLDER'], filename)
				file.save(filepath)
				dta = fun.read_table_files(filepath)
				if dta['error'] == 0:
					status = insert_data(dta['data'])
					if status:
						flash('File was uploaded and the content inserted into the database.', 'info')
						stage = 'stage3'
					else:
						flash('File was uploaded but the content could not be inserted into the database.', 'error')
						stage = 'stage3'
				else:
					flash('File was uploaded but the format is incorrect.', 'error')
					stage = 'stage2'
					data = dta['data']

		return render_template('add_file.html', stage = stage, data = data)
	else:
		redirect(url_for('main.profile'))


@main.route('/data_matrix')
def data_matrix():
	sex_t = get_sex()
	strain_t = get_strain()
	line_t = get_line()
	method_t = get_method()
	type_t = get_datatype()
	data = get_table()
	return render_template('data_matrix.html', matrix = data, sex_t = sex_t, \
		strain_t = strain_t, line_t = line_t, method_t = method_t, type_t = type_t)

@main.route('/about')
def about():
	return render_template('about.html')

# CREATING FLASK APPLICATION
###############################################################################

# Create and register the app
app = Flask(__name__)
app.config['SECRET_KEY'] = env['APP_SECRET']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + env['DDBB_USER'] + ':' + \
	env['DDBB_PASSWORD'] + '@' + env['DDBB_HOST'] + ':' + env['DDBB_PORT'] + \
	'/' + env['DDBB_NAME']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = env['APP_UPLOAD_FOLDER']
app.register_blueprint(auth)
app.register_blueprint(main)
#app.register_blueprint(api)

db.init_app(app)

# setting up the login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


# Set-up validation
@login_manager.user_loader
def load_user(user_id):
	# since the user_id is just the primary key of our user table, use it 
	# in the query for the user
	return User.query.get(int(user_id))

if __name__ == '__main__':
	app.run()
