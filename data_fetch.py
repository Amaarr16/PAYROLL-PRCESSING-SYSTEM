# data_fetch.py
from flask import Flask
from database import get_mysql_connection
from dotenv import load_dotenv
import os
load_dotenv()  # Load environment variables from .env file
app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Psatpsat')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'payroll_processing_system')

get_mysql_connection(app)

def fetch_employee_data(app):
    # Fetch and return Employee data
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Employee")
    employees = cursor.fetchall()
    connection.close()
    return employees

def fetch_attendance_data(app):
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Attendance")
    attendance = cursor.fetchall()
    connection.close()
    return attendance

def fetch_leave_data(app):
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM `Leave`")  # Use backticks around 'Leave'
    leave = cursor.fetchall()
    connection.close()
    return leave

def fetch_salary_calculation_data(app):
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SalaryCalculation")
    salary_calculations = cursor.fetchall()
    connection.close()
    return salary_calculations

def fetch_employer_data(app):
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Employer")
    employers = cursor.fetchall()
    connection.close()
    return employers

def fetch_all_data(app):
    employee_data = fetch_employee_data(app)
    attendance_data = fetch_attendance_data(app)
    leave_data = fetch_leave_data(app)
    salary_data = fetch_salary_calculation_data(app)
    employer_data = fetch_employer_data(app)
    # Fetch data for other tables similarly
    all_data = {
        'employee_data': employee_data,
        'attendance_data': attendance_data,
        'leave_data': leave_data,
        'salary_data':salary_data,
        'employer_data':employer_data
        # Include other table data similarly in the dictionary
        # Other tables similarly
    }
    return all_data