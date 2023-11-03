from flask import Flask, render_template, request, redirect, url_for, session, flash
#from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
import os
import mysql
import mysql.connector

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'a_secure_random_key_here'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Psatpsat'
app.config['MYSQL_DB'] = 'payroll_processing'  # Use the name of your database
# Remove this line, as you don't need it for 'mysql.connector'
#mysql = MySQL(app)
# Create a MySQL connection and cursor
def get_mysql_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
# Function to create the database if it doesn't exist
def create_database_if_not_exists():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS payroll_processing")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating the database: {e}")

create_database_if_not_exists()

def create_employee_table_if_not_exists():
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            emp_name VARCHAR(255),
            emp_designation VARCHAR(255),
            emp_dob DATE,
            emp_mobile_no VARCHAR(15),
            emp_email VARCHAR(255),
            emp_password VARCHAR(255)
        )
        """)

        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error creating 'employee' table: {e}")


@app.route('/')
def index():
    # Handle the index page
    # You can fetch data from the database and pass it to the template
    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # Handle the registration page
    if request.method == 'POST':
        emp_name = request.form['emp_name']
        emp_designation = request.form['emp_designation']
        emp_dob = request.form['emp_dob']
        emp_mobile_no = request.form['emp_mobile_no']
        emp_email = request.form['emp_email']
        # Handle the form submission and insert data into the database
        # You can use mysql to interact with the database
        # Create a MySQL connection and cursor
        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO employee (emp_name, emp_designation, emp_dob, emp_mobile_no, emp_email) VALUES (%s, %s, %s, %s, %s)",
            (emp_name, emp_designation, emp_dob, emp_mobile_no, emp_email)
        )
        # Execute SQL queries to insert data
        # Example: cursor.execute("INSERT INTO employee (emp_name, emp_designation, ...) VALUES (%s, %s, ...)", (form_data))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    return render_template('/registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_email = request.form['emp_email']
        emp_password = request.form['emp_password']

        # Create a MySQL connection and cursor
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)  # Fetch results as dictionaries
        cursor.execute("SELECT * FROM employee WHERE emp_email = %s", (emp_email,))
        user = cursor.fetchone()
        
        if user and user['emp_password'] == emp_password:
            # Authentication successful
            # You can set the user's session here
            session['user_id'] = user['emp_id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is authenticated
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    create_employee_table_if_not_exists()
    app.run(debug=True)
