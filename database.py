# database.py
from flask import Flask
import mysql.connector
app = Flask(__name__)
def get_mysql_connection(app):
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def create_database_if_not_exists(app):
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS payroll_processing_system")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating the database: {e}")

def create_employee_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employee (
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            emp_name VARCHAR(255),
            emp_designation VARCHAR(255),
            emp_dob DATE,
            emp_mobile_no VARCHAR(15),
            emp_email VARCHAR(255),
            emp_password VARCHAR(255),
            employer VARCHAR(255)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'employee' table: {e}")


def create_attendance_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            emp_id INT,
            present_days INT,
            absent_days INT,
            FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'attendance' table: {e}")

def create_leave_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Leave (
            emp_id INT,
            leave_type ENUM('Sick Leave', 'Casual Leave', 'Vacation Leave'),
            number_of_days INT,
            FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'leave' table: {e}")

def create_salary_calculation_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SalaryCalculation (
            emp_id INT,
            hra DECIMAL(10,2),
            da DECIMAL(10,2),
            ba DECIMAL(10,2),
            ta DECIMAL(10,2),
            incentive DECIMAL(10,2),
            total_salary DECIMAL(10,2),
            FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'salary_calculation' table: {e}")

def create_pays_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pays (
            emp_id INT,
            payment_amount DECIMAL(10,2),
            payment_date DATE,
            FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'pays' table: {e}")