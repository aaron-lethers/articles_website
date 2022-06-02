from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, request
# from data import articles 	# test data
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm, ArticleForm, EditForm
from functools import wraps

app = Flask(__name__)

# Config MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'articlesflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Init
mysql = MySQL(app)

# my_articles = articles()		# test data

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
	articles_list = []
	# create cur
	cur = mysql.connection.cursor()
	# create query and save result
	result = cur.execute("SELECT * FROM articles")
	articles = cur.fetchall()

	if result > 0:
		for article in articles:
			articles_list.append({'title': article['title'], 'body': article['body'], 'id': article['id']})
		return render_template('articles.html', articles=articles_list)
	else:
		msg = 'No Articles Found'
		return render_template('articles.html', msg=msg)

	print(articles_list)

	# title = result['title']
	return render_template('articles.html', articles=articles_list)

# SINGLE ARTICLE
@app.route('/article/<string:id>/')
def article(id):
	# create cur
	cur = mysql.connection.cursor()
	# create query and execute
	result = cur.execute("SELECT * FROM articles WHERE id=%s", ([id]))
	data = cur.fetchone()

	title = data['title']
	body = data['body']
	date = data['create_date']
	author = data['author']

	return render_template('article.html', title=title, body=body, author=author, date=date)

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

# Check if user is logged in
# https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if not session['logged_in']:
			flash('Must be logged in', 'danger')
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return wrap


# USER LOGOUT
@app.route('/logout')
@login_required
def logout():
	session.clear()
	session['logged_in'] = False

	flash("Logged out", 'success')
	return redirect(url_for('login'))

# USER DASHBOARD
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
	# create cur
	cur = mysql.connection.cursor()
	# get articles 
	result = cur.execute("SELECT * FROM articles WHERE author=%s", ([session['username']]))

	articles = cur.fetchall()

	if result > 0:
		return render_template('dashboard.html', articles=articles)
	else:
		msg = 'No articles found'
		return render_template('dashboard.html', msg=msg)

	# close connection
	cur.close()

# CREATE ARTICLES
@app.route('/create_article', methods=['POST', 'GET'])
@login_required
def create_article():
	form = ArticleForm(request.form)

	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		author = session['username']

		# open cursor
		cur = mysql.connection.cursor()
		# execute query
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, author))
		# commit to db
		mysql.connection.commit()
		# close cur
		cur.close()

		# redirect
		flash('Article created!', 'success')
		return redirect(url_for('dashboard'))

	return render_template('create_article.html', form=form)

@app.route('/edit_article/<string:id>', methods=['POST', 'GET'])
@login_required
def edit_article(id):
	form = EditForm(request.form)

	# open cursor
	cur = mysql.connection.cursor()
	# select query to prefill title and body form
	result = cur.execute("SELECT title, body FROM articles WHERE id=%s", ([id]))
	articles = cur.fetchone()
	cur.close()

	# print("result: ", result)
	# print("articles: ",articles)

	if request.method == 'POST' and form.validate():	
		title = form.title.data
		body = form.body.data
		# open cur
		cur = mysql.connection.cursor()
		# execute query -- this will be an update
		cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))
		# commit to db
		mysql.connection.commit()
		# close cur
		cur.close()
		flash('Updated article', 'success')
		return redirect(url_for('dashboard'))

	form.title.data = articles['title']
	form.body.data = articles['body']
	return render_template('edit_article.html', form=form, id=id)

@app.route('/delete_article/<string:id>', methods=['POST'])
@login_required
def delete_article(id):
	# Create cursor
	cur = mysql.connection.cursor()
	# execute delete query
	cur.execute("DELETE FROM articles WHERE id=%s", ([id]))
	# commit to db
	mysql.connection.commit()
	# close cur
	cur.close()

	flash('Article Deleted', 'success')
	return redirect(url_for('dashboard'))


if __name__ == '__main__':
	app.secret_key='secret_key'
	app.run(debug=True)