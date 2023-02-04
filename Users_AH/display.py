from datetime import date
from conn import app, mysql, render_template, request, redirect, session, url_for
import MySQLdb.cursors
import socket
import socket
from pprint import pprint

# http://localhost:5000/list- this will be the data list page
@app.route('/list')
def list():
        # Output message if something goes wrong...
        msg = 'Not data found'
        msgp = 'Not data found'
        # Check if user is lopgedin
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

    # http://localhost:5000/<it:id>/tmp- this will be redirect to template of report
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
                    "SELECT * FROM user WHERE username LIKE %s OR firstname LIKE %s OR name LIKE %s OR email LIKE %s OR phone LIKE %s OR date LIKE %s or role LIKE %s",
                    (search, search, search, search, search, search, search,))
                # Fetch one record and return result
                doctors = cursor.fetchall()
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    "SELECT * FROM patient WHERE firstname LIKE %s OR name LIKE %s OR email LIKE %s OR phone LIKE %s or date LIKE %s OR address LIKE %s OR city LIKE %s OR postal Like %s OR blood LIKE %s",
                    (search, search,search, search, search, search, search, search, search,))
                # Fetch one record and return result
                patients = cursor.fetchall()
                if doctors:
                    msg = ''
                if patients:
                    msg1 = ''
            return render_template('list.html', doctors=doctors, patients=patients, msg=msg, msg1=msg1)
        return redirect(url_for('login'))


# Function to scan port on the server
server="127.0.0.1"
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def scan(port):
    # Check the status of the port
    try:
        s.connect((server, port))  
        pprint(port)     
        return True
    except:       
        return False
    s.close()

# Function to go at page for the scanport
@app.route('/scan_page')
def scan_page():
    return render_template('scan.html')

# Function to display the results of the scanport()
@app.route('/scanports', methods=['POST'])
def scanports():
    if 'loggedin' in session:
        # Check datetime now with expired time account
        today = date.today().strftime('%Y-%m-%d')
        if session['date'] <= today:
            return redirect(url_for('update_pwd'))
        # Method verification and variable initialization 
        if request.method == 'POST':
            start = int(request.form['start'])
            end = int(request.form['end'])  
            scans={}
            # Inversion of variables if start is greater than end
            if start>end : 
                tmp=start
                start=end
                end=tmp
            # Verification loop of each chosen port
            for port in range(start,end+1):
                if scan(port):
                    scans[port]="open"
                else:
                    scans[port]="close"
                    continue
            return render_template('scan.html', scans=scans)
    return redirect(url_for('login'))