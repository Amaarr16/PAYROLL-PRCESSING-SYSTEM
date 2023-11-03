# database.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql
import mysql.connector
app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Psatpsat'
app.config['MYSQL_DB'] = 'payroll_processing'
# Create a MySQL connection and cursor
def get_mysql_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )