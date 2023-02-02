import MySQLdb.cursors
from datetime import date
from conn import app, mysql, render_template, redirect, session, url_for
import MySQLdb.cursors

import log

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
