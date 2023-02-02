from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL


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