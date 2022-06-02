from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, request
from data import articles 	# test data
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm

app = Flask(__name__)

# Config MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'articlesflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Init
mysql = MySQL(app)

my_articles = articles()		# test data

# HOME
@app.route('/')
def home():
	return render_template('home.html')

# ABOUT
@app.route('/about')
def about():
	return render_template('about.html')

# ALL ARTICLES
@app.route('/articles')
def articles():
	return render_template('articles.html', articles=my_articles)

# SINGLE ARTICLE
@app.route('/article/<string:id>/')
def article(id):
	body = my_articles[int(id)-1]['body']
	return render_template('article.html', id=id, body=body)

# USER REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)

	if request.method == 'POST' and form.validate():
		# not request.form['...'] -> specific for WTForms
		name = form.name.data # request.form['name']				
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.hash(str(form.password.data))

		# Create cursor
		cur = mysql.connection.cursor()

		# validate that this user does not already exist
		cur.execute("SELECT email FROM users WHERE email=%s", ([email]))
		rows = cur.fetchall()

		if len(rows) == 0:
			cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
			# Commit to DB
			mysql.connection.commit()
			# Close connection
			cur.close()
			flash("User Registered", 'success')
			return redirect(url_for('register'))
		else:
			flash("Email already used", 'danger')
			redirect(url_for('register'))

	return render_template('register.html', form=form)

# USER LOGIN
@app.route('/login', methods=['POST', 'GET'])
def login():
	form = LoginForm(request.form)
	# git comment

	if request.method == 'POST':
		# user posts form data -> compare form data to db
		if request.method == 'POST' and form.validate():
			email = form.email.data
			#cur_password = sha256_crypt.hash(str(form.password.data))
			cur_password = form.password.data
			# print(cur_password)

			# get password from db
			# verify password with user entered password. 
			# if good then logged in; else send error

			# Create cursor
			cur = mysql.connection.cursor()

			# Execuete query
			# cur.execute("SELECT name FROM users WHERE email=%s and password=%s", (email, password))
			result = cur.execute("SELECT * FROM users WHERE email=%s", ([email]))
			if result > 0:
				data = cur.fetchone()
				password = data['password']

				# print(str(password[0]['password']))

				if sha256_crypt.verify(cur_password, password):
					# log user in
					session['logged_in'] = True
					session['email'] = email 
					session['username'] = data['username']


					flash("Successfully logged in", 'success')
					return redirect(url_for('dashboard'))
				else:
					flash("Incorrect password", 'danger')
					return redirect(url_for('login'))

			else:
				flash("No user", 'danger')
				return redirect(url_for('login'))
			# Close connection
			cur.close()


	return render_template('login.html', form=form)

# USER LOGOUT
@app.route('/logout')
def logout():
	session.clear()
	session['logged_in'] = False

	flash("Logged out", 'success')
	return redirect(url_for('login'))

# USER DASHBOARD
@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():

	return render_template('dashboard.html', articles=my_articles)


if __name__ == '__main__':
	app.secret_key='secret_key'
	app.run(debug=True)