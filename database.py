# database.py (for database related functionalities)
import os
from flask import Flask
import mysql.connector
from dotenv import load_dotenv
app = Flask(__name__)
load_dotenv()

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Psatpsat')
def create_database_if_not_exists(app):
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        cursor = connection.cursor()
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS payroll_processing_system")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating the database: {e}")
create_database_if_not_exists(app)
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'payroll_processing_system')

def get_mysql_connection(app):
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def create_employee_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employee (
            emp_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            f_name VARCHAR(255) NOT NULL,
            m_name VARCHAR(255) NOT NULL, 
            l_name VARCHAR(255) NOT NULL,
            emp_designation VARCHAR(255) NOT NULL,
            emp_dob DATE NOT NULL,
            emp_mobile_no VARCHAR(15) NOT NULL,
            emp_email VARCHAR(255),
            acc_name VARCHAR(255) NOT NULL,
            acc_number VARCHAR(255) NOT NULL,
            ifsc_Code VARCHAR(255) NOT NULL,
            emp_ver_id INT NOT NULL,
            emp_password VARCHAR(255) NOT NULL,
            verification_status ENUM('Pending', 'Verified', 'Rejected') NOT NULL,
            oth_emp_id INT DEFAULT '0',
            employer VARCHAR(255) NOT NULL
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'Employee' table: {e}")

def create_attendance_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            a_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
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
        CREATE TABLE IF NOT EXISTS `Leave` (
            emp_id INT,
            leave_type ENUM('Sick Leave', 'Casual Leave', 'Vacation Leave') DEFAULT 'Sick Leave',
            number_of_days INT,
            FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'leave' table: {e}")

def create_employer_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employer(
            empl_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            empl_desg VARCHAR(255) NOT NULL,
            empl_mob_no VARCHAR(255) NOT NULL,
            empl_depart VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'employer' table: {e}")

def create_salary_calculation_table_if_not_exists(app):
    try:
        connection = get_mysql_connection(app)
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS SalaryCalculation (
            s_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
            emp_id INT ,
            empl_id INT NOT NULL,
            hra DECIMAL(10,2),
            da DECIMAL(10,2),
            ba DECIMAL(10,2),
            ta DECIMAL(10,2),
            incentive DECIMAL(10,2),
            total_salary DECIMAL(10,2),
            net_salary DECIMAL(10,2),
            FOREIGN KEY (emp_id) REFERENCES Employee(emp_id),
            FOREIGN KEY (empl_id) REFERENCES Employer(empl_id)
        )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating 'salary_calculation' table: {e}")

# Other table creation functions...

def create_all_tables(app):
    # Function to create all tables
    create_employee_table_if_not_exists(app)
    create_attendance_table_if_not_exists(app)
    create_leave_table_if_not_exists(app)
    create_employer_table_if_not_exists(app)
    create_salary_calculation_table_if_not_exists(app)
    