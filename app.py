from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'a_secure_random_key_here'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Psatpsat'
app.config['MYSQL_DB'] = 'payroll_processing'  # Use the name of your database

def get_mysql_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

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
            emp_password VARCHAR(255),
            employer VARCHAR(255),
            employer_logo_url VARCHAR(255)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'employee' table: {e}")

create_employee_table_if_not_exists()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        emp_name = request.form['emp_name']
        emp_designation = request.form['emp_designation']
        emp_dob = request.form['emp_dob']
        emp_mobile_no = request.form['emp_mobile_no']
        emp_email = request.form['emp_email']
        emp_password = request.form['emp_password']
        employer='Payroll Processing System'
        employer_logo_url='PAYROLL-IMG.jpg'
        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO employee (emp_name, emp_designation, emp_dob, emp_mobile_no, emp_email, emp_password, employer, employer_logo_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (emp_name, emp_designation, emp_dob, emp_mobile_no, emp_email, emp_password, employer, employer_logo_url)
            )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_email = request.form['emp_email']
        emp_password = request.form['emp_password']
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee WHERE emp_email = %s", (emp_email,))
        user = cursor.fetchone()
        if user and user['emp_password'] == emp_password:
            session['user_id'] = user['emp_id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee WHERE emp_id = %s", (session['user_id'],))
        employee = cursor.fetchone()
        connection.close()
        if employee:
            employer_logo_url = employee.get('employer_logo_url', '')
            return render_template('dashboard.html', employee=employee, employer_logo_url=employer_logo_url)
        else:
            return "Employee not found"
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user_id from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_employee_table_if_not_exists()
    app.run(debug=True)
