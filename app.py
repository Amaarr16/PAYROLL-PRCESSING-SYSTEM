
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from database import get_mysql_connection, create_database_if_not_exists, create_employee_table_if_not_exists
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
print(os.environ)
app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'a_secure_random_key_here'

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Psatpsat')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'payroll_processing_system')
#create_database_if_not_exists(app)
#create_employee_table_if_not_exists(app)

#FUNCTION FOR INDEX PAGE
@app.route('/')
def index():
    return render_template('index.html')

#FUNCTION FOR REGISTRATION PAGE
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        emp_name = request.form['emp_name']
        emp_designation = request.form['emp_designation']
        emp_dob = request.form['emp_dob']
        emp_mobile_no = request.form['emp_mobile_no']
        emp_email = request.form['emp_email']
        emp_password = generate_password_hash(request.form['emp_password'], method='pbkdf2:sha1')
        employer='Payroll Processing System'
        #employer_logo_url='PAYROLL-IMG.jpg'
        connection = get_mysql_connection(app)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO employee (emp_name, emp_designation, emp_dob, emp_mobile_no, emp_email, emp_password, employer) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (emp_name, emp_designation, emp_dob, emp_mobile_no, emp_email, emp_password, employer)
            )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    return render_template('registration.html')

#FUNCTION FOR LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emp_email = request.form['emp_email']
        emp_password = request.form['emp_password']
        connection = get_mysql_connection(app)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee WHERE emp_email = %s", (emp_email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['emp_password'], emp_password):
            session['user_id'] = user['emp_id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html', flask_secret_key=os.environ.get('FLASK_SECRET_KEY'))

#FUNCTION FOR DASHBORD PAGE
@app.route('/dashboard') 
def dashboard():
    if 'user_id' in session:
        connection = get_mysql_connection(app)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee WHERE emp_id = %s", (session['user_id'],))
        employee = cursor.fetchone()
        connection.close()
        if employee:
            #employer_logo_url = employee.get('employer_logo_url', '')
            return render_template('dashboard.html', employee=employee)#, employer_logo_url=employer_logo_url)
        else:
            return "Employee not found"
    else:
        return redirect(url_for('login'))

#FUNCTION FOR LOGOUT PAGE
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user_id from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    get_mysql_connection(app)
    create_database_if_not_exists(app)
    create_employee_table_if_not_exists(app)
    app.run(debug=True)
