from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from pprint import pprint
from datetime import date, timedelta, datetime
import random
import string
import hashlib

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
        # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
            return redirect(url_for('update_pwd'))
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        id = session['id']
        cursor.execute(
            'SELECT * FROM user WHERE id = %s', (id,))
        # Fetch one record and return result
        account = cursor.fetchone()
        return render_template('home.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/login - the following will be our login page, which will use both GET and POST requests


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        if username is None:
            msg = 'Please enter an username'
        password = request.form['password']
        if password is None:
            msg = 'Please enter an password'
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['role'] = account['role']
            session['date'] = account['date'].strftime('%Y-%m-%d')
            # Check datetime now with expired time account
            today = date.today().strftime('%Y-%m-%d')
            if session['date'] <= today :
                return redirect(url_for('update_pwd'))
            # Check if account actived
            if account['actived'] == 0:
                msg = 'Account not actived'
                return render_template('index.html', msg=msg)
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

# http://localhost:5000/register/doctor - this will be the register doctor page, we need to use both GET and POST requests


@app.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        # Check if POST requests exist
        if request.method == 'POST':
            # Create variables for easy access
            name = request.form['name']
            firstname = request.form['firstname']
            # Create username with name and firstname
            username = firstname[0] + name
            phone = request.form['phone']
            # expired date
            today = date.today().strftime('%Y-%m-%d')
            # 3 roles : Supervisor, Administrator, Doctor
            role = request.form['role']
            # Generate pwd et hash
            password = request.form['password']
            email = request.form['email']
            # Check if username exists
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM user WHERE username = %s', (username,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Account already exists!'
            # Regex email
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            # Regex name
            elif not re.match(r'[A-Za-z]+', name):
                msg = 'Name must contain only characters !'
            # Regex fistname
            elif not re.match(r'[A-Za-z]+', firstname):
                msg = 'Firstname must contain only characters !'
            # Check if variable not null
            elif username is None or name is None or firstname is None or phone is None or today is None or password is None or email is None:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO user VALUES (0, %s, %s, %s, %s, %s, %s, 0, %s, %s)',
                               (username, name, firstname, email, phone, today, password, role,))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('register/doctor.html', msg=msg)
    return redirect(url_for('login'))

# http://localhost:5000/register/patient - this will be the register patient page, we need to use both GET and POST requests


@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        # Check if POST requests exist
        if request.method == 'POST':
            # Create variables for easy access
            file = request.form['file']
            name = request.form['name']
            firstname = request.form['firstname']
            description = request.form['description']
            drug = request.form['drug']
            expire = request.form['date']
            # Check if username exists
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM patient WHERE file = %s', (file,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Patient already exists!'
            # Regex file
            elif not re.match(r'[0-9]+', file):
                msg = 'File must contain only numbers!'
            # Check form
            elif file is None or name is None or firstname is None or description is None or drug is None or expire is None:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO patient VALUES (0, %s, %s, %s, %s, %s, %s)',
                               (file, name, firstname, description, drug, expire,))
                mysql.connection.commit()
                msg = 'You have successfully registered!'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('register/patient.html', msg=msg)
    return redirect(url_for('login'))

# http://localhost:5000/list- this will be the data list page


@app.route('/list')
def list():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        # Select data from user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        # Fetch one record and return result
        doctors = cursor.fetchall()

        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM patient')
        # Fetch one record and return result
        patients = cursor2.fetchall()
        return render_template('list.html', doctors=doctors, patients=patients, msg=msg)
    return redirect(url_for('login'))

# http://localhost:5000/search- this will be the search data in a list page


@app.route('/search', methods=['GET'])
def search():
    # Output message if something goes wrong...
    msg = 'Not data found'
    msg1 = 'Not data found'
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        if request.method == "GET":
            search = request.args.get("q")
            search = "%{}%".format(search)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM user WHERE username LIKE %s OR firstname LIKE %s OR name LIKE %s OR email LIKE %s OR phone LIKE %s",
                (search, search, search, search, search))
            # Fetch one record and return result
            doctors = cursor.fetchall()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM patient WHERE firstname LIKE %s OR name LIKE %s",
                (search, search))
            # Fetch one record and return result
            patients = cursor.fetchall()
            if doctors:
                msg = ''
            if patients:
                msg1 = ''
        return render_template('list.html', doctors=doctors, patients=patients, msg=msg, msg1=msg1)
    return redirect(url_for('login'))

# http://localhost:5000/logout - this will be the logout page


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('date', None)
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/<int:id>/delete - this will be delete the id post


@app.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        if request.method == 'POST':
            # We need all the account info for the user so we can display it on the profile page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM user WHERE id = %s', (id,))
            mysql.connection.commit()
            # Show the profile page with account info
            return redirect(url_for('list'))
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/<int:id>/update_doctor - this will be update the id doctor's


@app.route('/<int:id>/update_doctor', methods=['GET', 'POST'])
def update_doctor(id):
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (id,))
        doctor = cursor.fetchone()
        if request.method == 'POST':
            if doctor:
                # delete before create with same id
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('DELETE FROM user WHERE id = %s',
                               (doctor['id'],))
                mysql.connection.commit()
                # Create variables for easy access
                name = request.form['name']
                firstname = request.form['firstname']
                phone = request.form['phone']
                username = firstname[0] + name
                expire = request.form['date']
                role = 'Admin'
                password = request.form['password']
                email = request.form['email']
                # Regex email
                if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address!'
                # Check if variable not null
                elif username is None or name is None or firstname is None or phone is None or expire is None or password is None or email is None:
                    msg = 'Please fill out the form!'
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s, %s)',
                                   (id, username, name, firstname, email, phone, expire, password, role,))
                    mysql.connection.commit()
                    return redirect(url_for('list'))
    return render_template('update/doctor.html', doctor=doctor, msg=msg)

# http://localhost:5000/<int:id>/update_patient - this will be update the id patient's


@app.route('/<int:id>/update_patient', methods=['GET', 'POST'])
def update_patient(id):
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check if expired password
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today :
            return redirect(url_for('update_pwd'))
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient WHERE id = %s', (id,))
        patient = cursor.fetchone()
        if request.method == 'POST':
            if patient:
                # delete before create with same id
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('DELETE FROM patient WHERE id = %s',
                               (patient['id'],))
                mysql.connection.commit()
                # Create variables for easy access
                file = request.form['file']
                name = request.form['name']
                firstname = request.form['firstname']
                description = request.form['description']
                drug = request.form['drug']
                expire = request.form['date']
                # Check if variable not null
                if name is None or firstname is None or file is None or expire is None or drug is None or description is None:
                    msg = 'Please fill out the form!'
                else:
                    # now insert update into patient table
                    cursor.execute('INSERT INTO user VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s, %s)',
                                   (id, description, name, firstname, file, drug, expire,))
                    mysql.connection.commit()
                    return redirect(url_for('list'))
    return render_template('update/patient.html', patient=patient, msg=msg)

# http://localhost:5000/<int:id>/change_pwd - this will be update the id user's password


@app.route('/change_pwd', methods=['GET', 'POST'])
def update_pwd():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        id = session['id']
        cursor.execute('SELECT * FROM user WHERE id = %s', (id,))
        account = cursor.fetchone()
        if request.method == 'POST':
            if account:
                # Add 30 days
                delta = datetime.now() + timedelta(days=30)
                expire = delta.strftime('%Y-%m-%d')
                # create variables for easy access
                old = request.form['old']
                password = request.form['password']
                if old != account['password']:
                    msg = 'Incorrect password !'
                # Check if variable not null or password is the same
                elif password is None or password == account['password']:
                    msg = 'Use a new password to change !'
                else:
                    # now insert an update column into user table
                    cursor.execute('UPDATE user SET date = %s, password = %s',
                                   (expire, password,))
                    mysql.connection.commit()
                    # Update session :
                    session['date'] = expire
                    return redirect(url_for('home'))
    return render_template('update/password.html', msg=msg)

# function random password
def generate_pwd():
    alphanumeric = string.ascii_letters+string.digits
    pwd = ""
    for i in range(10):
        pwd = pwd + alphanumeric[random.randint(0,len(alphanumeric))]
    return pwd

# function hash
def hash_pwd(pwd):
    pwd_crypte = hashlib.md5(pwd.encode()).hexdigest()
    return pwd_crypte
