from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from pprint import pprint
from datetime import date, timedelta, datetime
import random
import string
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

# Variable Global for tries login 
tries=3

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
    global tries
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        if username is None:
            msg = 'Please enter an username'
        password = request.form['password']
        encrypt = hash_pwd(password)
        if password is None:
            msg = 'Please enter an password'
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Check if account actived
            if account['actived'] == 0:
                msg = 'Account not actived ! Contact your Administrator'
            elif username==account['username'] and encrypt != account['password']:
                tries=int(tries)-1
                es=" try !" if tries==1 else " tries !"
                msg = 'Incorrect password ! \n You have more than ' + str(tries) + es
            else :
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                session['role'] = account['role']
                session['date'] = account['expire'].strftime('%Y-%m-%d')
                # Check datetime now with expired time account
                today = date.today().strftime('%Y-%m-%d')
                if session['date'] <= today :
                    return redirect(url_for('update_pwd'))
                return redirect(url_for('home'))       
        else:
            # Account doesnt exist or username/password incorrect          
            msg = 'Incorrect username !'
        # If he have doing 3 tries
        if tries==0:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE user SET actived=0 where username=%s', (account['username'],))
            # Fetch one record and return result
            mysql.connection.commit()
            msg = 'You have disable your account ! Contact your Administrator'
            tries=3
    return render_template('index.html', msg=msg)

# http://localhost:5000/register/doctor - this will be the register doctor page, we need to use both GET and POST requests
@app.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        if session['role'] == 'Admin' or session['role'] == 'Supervisor': 
            # Check datetime now with expired time account
            today = date.today().strftime('%Y-%m-%d')
            if session['date'] <= today:
                return redirect(url_for('update_pwd'))
            # Check if POST requests exist
            if request.method == 'POST':
                # Create variables for easy access
                name = request.form['name']
                firstname = request.form['firstname']
                # Create username with name and firstname
                dat = request.form['date']
                username = firstname[0] + name.lower()
                phone = request.form['phone']
                # expired date
                today = date.today().strftime('%Y-%m-%d')
                # 3 roles : Supervisor, Administrator, Doctor
                role = request.form['role']
                # Generate pwd et hash
                password = generate_pwd()
                encrypt = hash_pwd(password)
                email = request.form['email']
                # Check if username exists
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'SELECT * FROM user WHERE name=%s AND firstname=%s AND date=%s OR username=%s OR email=%s', (name, firstname, dat, username, email,))
                account = cursor.fetchone()
                # Check admin create
                curs = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                curs.execute(
                    'SELECT COUNT(role) FROM `user` WHERE role = "Admin"')
                count = curs.fetchone()
                if account:
                    # If account exists show error and validation checks
                    if account['name']==name and account['firstname']==firstname and account['date']==dat:
                        msg = 'Account already exists!'
                    # Regex email
                    elif account['email']==email:
                        msg = 'Email already exists!'
                    # If user have the same 1 lettre of firstname and same name
                    elif account['username']==username:
                        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                        y=username+"%"
                        cursor.execute(
                            'SELECT username FROM user WHERE username Like %s ORDER BY username DESC LIMIT 1', (y,))
                        account = cursor.fetchone()
                        use=account['username']
                        usez = use[-1]
                        if ord(usez) not in range(48,57):
                            i=1
                            username = username + str(i)
                        else:
                            username = use[:-1] + str((int(usez) + 1))
                if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address!'
                # Regex name
                elif not re.match(r'[A-Za-z]+', name):
                    msg = 'Name must contain only characters !'
                # Regex fistname
                elif not re.match(r'[A-Za-z]+', firstname):
                    msg = 'Firstname must contain only characters !'
                # Check if variable not null
                elif username is None or name is None or firstname is None or phone is None or password is None or email is None or dat is None:
                    msg = 'Please fill out the form!'
                # Check if 4 admins created
                elif count['COUNT(role)'] > 4:
                    msg = 'Admin rate has been reached !'
                else:          
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO user VALUES (0, %s, %s, %s, %s, %s, %s, 0, %s, %s, %s)',
                                (username, name, firstname, email, phone, dat, encrypt, role, today,))
                    mysql.connection.commit()
                    connection_mail(email, username, password)
                    msg = 'You have successfully registered!'

            elif request.method == 'POST':
                # Form is empty... (no POST data)
                msg = 'Please fill out the form!'
            # Show registration form with message (if any)
            dat=date.today().strftime('%Y-%m-%d')
            return render_template('register/doctor.html', msg=msg, dat=dat)
    return redirect(url_for('login'))

# http://localhost:5000/register/patient - this will be the register patient page, we need to use both GET and POST requests
@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        if session['role'] != 'Admin' or session['role'] != 'Supervisor': 
            # Check datetime now with expired time account
            today = date.today().strftime('%Y-%m-%d')
            if session['date'] <= today:
                return redirect(url_for('update_pwd'))
            # Check if POST requests exist
            if request.method == 'POST':
                # Create variables for easy access
                name = request.form['name']
                firstname = request.form['firstname']
                dat = request.form['date']
                email = request.form['email']
                phone = request.form['phone']
                address = request.form['address']
                city = request.form['city']
                postal = request.form['postal']
                blood = request.form['blood']
                doctor = session['id']

                # Check if username exists
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'SELECT * FROM patient WHERE name = %s AND firstname = %s AND date = %s', (name, firstname, dat,))
                account = cursor.fetchone()
                # If account exists show error and validation checks
                if account:
                    msg = 'Patient already exists!'
                # Check form
                elif email is None or city is None or postal is None or address is None or blood is None or doctor is None or name is None or firstname is None or phone is None or address is None or dat is None:
                    msg = 'Please fill out the form!'
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO patient VALUES (0, %s, %s, %s, %s, %s, %s ,%s, %s, %s, %s)',
                                (name, firstname, dat, email, phone, address, city, postal, blood, doctor,))
                    mysql.connection.commit()
                    msg = 'You have successfully registered!'
            elif request.method == 'POST':
                # Form is empty... (no POST data)
                msg = 'Please fill out the form!'
            # Show registration form with message (if any)
            dat=date.today().strftime('%Y-%m-%d')
            return render_template('register/patient.html', msg=msg, dat=dat)
    return redirect(url_for('login'))

# http://localhost:5000/list- this will be the data list page
@app.route('/list')
def list():
    # Output message if something goes wrong...
    msg = 'Not data found'
    msgp = 'Not data found'
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
            return redirect(url_for('update_pwd'))
        # Select data from user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        # Fetch one record and return result
        doctors = cursor.fetchall()
        if doctors:
            msg = ''
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute('SELECT * FROM patient')
        # Fetch one record and return result
        patients = cursor2.fetchall()
        if patients:
            msgp = ''
        return render_template('list.html', doctors=doctors, patients=patients, msgp=msgp, msg=msg)
    return redirect(url_for('login'))

# http://localhost:5000/<it:id>/register/report- this will be create a new report
@app.route('/register/report', methods=['GET', 'POST'])
def new_report():
    # Check if user is loggedin
    if 'loggedin' in session:
        if session['role'] != 'Admin' or session['role'] != 'Supervisor': 
            # Check datetime now with expired time account
            today = date.today().strftime('%Y-%m-%d')
            if session['date'] <= today:
                return redirect(url_for('update_pwd'))
            # Check if POST requests exist
            if request.method == 'POST':
                # Create variables for easy access
                description = request.form['description']
                drug = request.form['drug']
                id = request.form['id']
            # Select data from user
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO report VALUES (0, %s, %s, %s, %s)', (description, drug, today, id,))
            mysql.connection.commit()
            
            # Fetch one record and return result
            return redirect(url_for('report', id=id))
    return redirect(url_for('login'))

@app.route('/<int:id>/tmp', methods=['GET', 'POST'])
def tmp(id):
    return render_template('register/report.html' , id=id)

# http://localhost:5000/<it:id>/report- this will be list the report of an patient
@app.route('/<int:id>/report', methods=['GET', 'POST'])
def report(id):
    # Output message if something goes wrong...
    msg = 'Not data found'
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
            return redirect(url_for('update_pwd'))
        # Select data from user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM patient where id = %s', (id,))
        # Fetch one record and return result
        patient = cursor.fetchone()

        # Select all reports 
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('SELECT * FROM report where userid = %s'  , (id,))
        # Fetch one record and return result
        reports = cursor1.fetchall()
        if reports:
            msg = ''
        return render_template('reports.html', patient=patient, reports=reports, msg=msg)
    return redirect(url_for('login'))

# http://localhost:5000/<int:id>/active- this will be active the account
@app.route('/<int:id>/active', methods=['GET','POST'])
def active(id):
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'POST':
            # Active / Désactive
            active=request.form['enable']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    
            cursor.execute('UPDATE user SET actived=%s where id=%s',
                                        (active, id,))
            mysql.connection.commit()
            return redirect(url_for('list'))
    return redirect(url_for('login'))

# http://localhost:5000/search- this will be the search data in a list page
@app.route('/search', methods=['GET'])
def search():
    # Output message if something goes wrong...
    msg = 'Not data found'
    msg1 = 'Not data found'
    # Check if user is loggedin
    if 'loggedin' in session:
         # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
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
    session.clear()
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
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
@app.route('/<int:id>/delete', methods=['GET','POST'])
def delete(id):
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'POST':
            # We need all the account info for the user so we can display it on the profile page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            type = request.form['type']
            if type=='user':
                cursor.execute('DELETE FROM user WHERE id = %s', (id,))
            else:
                cursor.execute('DELETE FROM patient WHERE id = %s', (id,))
                mysql.connection.commit()
                cursor.execute('DELETE FROM report WHERE userid = %s', (id,))
                mysql.connection.commit()
            # Show the profile page with account info
            return redirect(url_for('list'))
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/<int:id>/update - this will be update the id and the type (user or patient)
@app.route('/<int:id>/<type>/update', methods=['GET', 'POST'])
def update(id,type):
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
         # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
            return redirect(url_for('update_pwd'))       
        # We need all the account info for the user so we can display it on the profile page
        if type=='user':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE id = %s', (id,))
            doctor = cursor.fetchone()
            if request.method == 'POST':
                if doctor:
                    # Create variables for easy access
                    phone = request.form['phone']
                    password = request.form['password']
                    encrytp=hash_pwd(password)
                    if encrytp!=doctor['password']:
                        delta = datetime.now() + timedelta(days=30)
                        expire = delta.strftime('%Y-%m-%d')
                    else : 
                        expire = doctor['expire']
                    email = request.form['email']
                    # Regex email
                    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Invalid email address!'
                    # Check if variable not null
                    elif phone is None or expire is None or password is None or email is None:
                        msg = 'Please fill out the form!'
                    else:
                        # Account doesnt exists and the form data is valid, now insert new account into accounts table
                        cursor.execute('UPDATE user SET email=%s, phone=%s, expire=%s, password=%s where id=%s',
                                    (email, phone, expire, encrytp, id,))
                        mysql.connection.commit()
                        return redirect(url_for('list'))
        else :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM patient WHERE id = %s', (id,))
            patient = cursor.fetchone()
            if request.method == 'POST':
                # Create variables for easy access
                email = request.form['email']
                phone = request.form['phone']
                address = request.form['address']
                city = request.form['city']
                postal = request.form['postal']
                # Check if variable not null
                if email is None or phone is None or address is None or city is None or postal is None :
                     msg = 'Please fill out the form!'
                else:
                    # now insert update into patient table
                    cursor.execute('UPDATE patient SET email=%s, phone=%s, address=%s, city=%s, postal=%s where id=%s',
                                (email, phone, address, city, postal, id, ))
                    mysql.connection.commit()
                    return redirect(url_for('list'))
    if type=='user':
        return render_template('update/doctor.html', doctor=doctor, msg=msg)
    else:
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
                old = hash_pwd(old)
                password = request.form['password']
                encrypt = hash_pwd(password)
                if old != account['password']:
                    msg = 'Incorrect password !'
                # Check if variable not null or password is the same
                elif password is None or password == account['password']:
                    msg = 'Use a new password to change !'
                else:
                    # now insert an update column into user table
                    cursor.execute('UPDATE user SET expire = %s, password = %s, actived = 1 WHERE id=%s',
                                   (expire, encrypt,session['id'],))
                    mysql.connection.commit()
                    # Update session :
                    session['date'] = expire
                    return redirect(url_for('home'))
    return render_template('update/password.html', msg=msg)

# function random password
def generate_pwd():
    alphanumeric = string.ascii_letters+string.digits # concatenation of usable letters
    pwd = "" # Initialisation variable
    for i in range(12):
        pwd = pwd + alphanumeric[random.randint(0,len(alphanumeric)-1)] # Random letter generation loop
    return pwd

# function hash
def hash_pwd(pwd):
    salt = "Python" #key hash
    pwd_crypte = hashlib.md5(pwd.encode()+salt.encode()).hexdigest() # encode passord
    return pwd_crypte

# Function email
def connection_mail(mail, username, pwd):
    message = MIMEMultipart()   #parse information email
    message['From'] = "testmaileur111@gmail.com"
    message['To'] = mail
    message['Subject'] = 'Activation compte American Hopital'
    message.attach(MIMEText("Bonjour, votre login est " + username +  " et votre mot de passe provisoire est  : " + pwd + ". \n Attention, il expire à 00h00 \nCordialement, American Hostipal", 'html')) # attachment body
    text = message.as_string() # text binding
    mailserver = smtplib.SMTP_SSL('smtp.gmail.com', 465) # connection SMTP Gmail
    mailserver.login('testmaileur111@gmail.com','ownjdlhlgviqchho') # connection account Gmail
    mailserver.sendmail('testmaileur111@gmail.com', mail,  text) # Send mail
    mailserver.quit() # close connection