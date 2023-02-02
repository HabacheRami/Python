from conn import app, mysql, render_template, request, redirect, session, url_for
import MySQLdb.cursors
import re
from datetime import date, timedelta, datetime

import log


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
                    password = log.generate_pwd()
                    encrypt = log.hash_pwd(password)
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
                        log.connection_mail(email, username, password)
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
                        encrytp=log.hash_pwd(password)
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