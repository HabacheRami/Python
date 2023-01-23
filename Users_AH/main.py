from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from pprint import pprint

app = Flask(__name__)

# Secret_key protection against cookie data tampering.
app.secret_key = 'python3projet'

# Database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'hospital'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/ - this will be the home page, only accessible for loggedin users


@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        id = session['id']
        cursor.execute(
            'SELECT * FROM user WHERE id = %s', (id,) )
        # Fetch one record and return result
        account = cursor.fetchone()
        pprint(account)
        return 'already log'
        #return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/login - the following will be our login page, which will use both GET and POST requests


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        if username is None:
            msg = 'Please enter an username'
        password = request.form['password']
        if password is None:
            msg= 'Please enter an password'
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            if account['actived'] == 0:
                msg = 'Account not actived'
                return render_template('index.html', msg=msg)
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))
