# database.py
import mysql.connector
from flask_bcrypt import Bcrypt

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
