from flask import Flask, render_template, session, request, redirect, flash
import re
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)  
app.secret_key = 'ThisIsSecret'
mysql = MySQLConnector('wall_python')
bcrypt = Bcrypt(app)

@app.route('/')                           
def index():
	return render_template('log_reg.html')

@app.route('/post_comment/<messageID>', methods=['POST'])
def post_comment(messageID):
	post = request.form
 	user_id = int(session['user'][0]['id'])
 	if not post['comment']:
 		return redirect('/display_wall')
 	else:
 		query = "INSERT INTO comments (comment, updated_at, created_at, message_id, user_id) VALUES ('{}', NOW(), NOW(), '{}', '{}')".format(post['comment'], messageID, user_id)
 		mysql.run_mysql_query(query)
		return redirect('/display_wall')

@app.route('/post_message', methods=['POST'])
def post_message():
	post = request.form
 	user_id = int(session['user'][0]['id'])

	if not post['message']:
		return redirect('/display_wall')
	else:
		# insert the message into the database
		query = "INSERT INTO messages (message, updated_at, created_at, user_id) VALUES ('{}', NOW(), NOW(), '{}')".format(post['message'], user_id)
		mysql.run_mysql_query(query)
		# return to the display_wall page
		return redirect('/display_wall')

@app.route('/display_wall')
def display_wall():
	query = "SELECT users.first_name as first_name, users.last_name as last_name, messages.created_at as created_at, messages.message as message, messages.id as message_id FROM messages JOIN users ON users.id = messages.user_id ORDER BY messages.created_at ASC"
	messages = mysql.fetch(query)

	query = "SELECT users.first_name as first_name, users.last_name as last_name, comments.created_at as created_at, comments.comment as comment, comments.id as comment_id, comments.message_id as comment_message_id FROM comments JOIN users ON users.id = comments.user_id ORDER BY comments.created_at DESC"
	comments = mysql.fetch(query)
	return render_template('success.html', messages = messages, comments = comments)

@app.route('/login', methods=['POST'])
def login():

	post = request.form
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

	if not post['email'] and not post['password']:
		flash('all texts must be filled')
	elif not EMAIL_REGEX.match(post['email']):
		flash('not a valid email')
	else:
		#select from database where email = post['email']
		query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(post['email'])
		user = mysql.fetch(query)
		#if it exists, redirect to success.html
		if user: 
			password = post['password']
			if bcrypt.check_password_hash(user[0]['password'], password):
				session['user'] = user
				print session['user']
				return redirect('/display_wall')
		#if it doesn't exist, redirect to index.html
		else:
			flash("info does not match")
	
	return redirect('/')

@app.route('/register', methods=['POST'])
def register():

	post = request.form
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')

	if not post['first_name']: 
		flash('first_name cannot be blank')
	elif post['first_name'].isalpha() == False:
		flash('first_name should only contain letters')
	elif len(post['first_name'])<2:
		flash('first_name is too short')

	elif not post['last_name']:
		flash('last_name cannot be blank')
	elif post['last_name'].isalpha() == False:
		flash('last_name should only contain letters')
	elif len(post['last_name'])<2:
		flash('last_name is too short')

	elif not post['email']:
		flash('email cannot be blank')
	elif not EMAIL_REGEX.match(post['email']):
		flash('email is not valid')

	elif not post['password']:
		flash('password cannot be blank')
	elif len(post['password'])<8:
		flash('password too short ')
	elif not post['password'] == post['confirm_password']:
		flash('confirm_password should match password')
	elif not post['confirm_password']:
		flash('confirm_password cannot be blank')
	else:
		password = post['password']

		# select from database where email = post['email']
		query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(post['email'])
		user = mysql.fetch(query)

		if user: 
			if bcrypt.check_password_hash(user[0]['password'], password):
				flash('user already exists')
		else:
		# if email doesn't exist in database, insert into database
			pw_hash = bcrypt.generate_password_hash(password)
			query = "INSERT INTO users (first_name, last_name, email, password, updated_at, created_at) VALUES ('{}', '{}', '{}', '{}', NOW(), NOW())".format(post['first_name'], post['last_name'], post['email'], pw_hash)
			mysql.run_mysql_query(query)
			flash('Successfully registered!')

	return redirect('/')
app.run(debug=True) 