from datetime import date, timedelta, datetime
import random, string, hashlib, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from conn import app, mysql, render_template, request, redirect, url_for, session
import MySQLdb.cursors

import display 
import user
import main

tries=3

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

    # http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
        # Remove session data, this will log the user out
        session.clear()
        # Redirect to login page
        return redirect(url_for('login'))

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
