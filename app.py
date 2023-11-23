from database import create_attendance_table_if_not_exists, create_leave_table_if_not_exists, create_pays_table_if_not_exists, create_salary_calculation_table_if_not_exists, get_mysql_connection, create_database_if_not_exists, create_employee_table_if_not_exists
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
#print(os.environ)

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'a_secure_random_key_here'

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Psatpsat')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'payroll_processing_system')

create_database_if_not_exists(app)
create_employee_table_if_not_exists(app)
create_salary_calculation_table_if_not_exists(app)
create_pays_table_if_not_exists(app)
create_attendance_table_if_not_exists(app)
create_leave_table_if_not_exists(app)

#FUNCTION FOR INDEX PAGE
@app.route('/')
def index():
    return render_template('index.html')

#FUNCTION FOR REGISTRATION PAGE
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        f_name = request.form['f_name']
        m_name = request.form['m_name']
        l_name = request.form['l_name']
        emp_designation = request.form['emp_desig']
        emp_dob = request.form['emp_dob']
        emp_mobile_no = request.form['emp_mobile_no']
        emp_email = request.form['emp_email']
        acc_name = request.form['acc_name']
        acc_number = request.form['acc_number']
        ifsc_code = request.form['ifsc_code']
        emp_password = generate_password_hash(request.form['emp_password'], method='pbkdf2:sha1')
        # Assuming you're the first member registering as an admin
        oth_emp_id_value = '0'  # For example, using None for absence of another employee ID
        #employer_logo_url='PAYROLL-IMG.jpg'
        connection = get_mysql_connection(app)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Employee (f_name, m_name, l_name, emp_designation, emp_dob, emp_mobile_no, emp_email, acc_name, acc_number, ifsc_code, emp_password, verification_status, oth_emp_id, employer) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (f_name, m_name, l_name, emp_designation, emp_dob, emp_mobile_no, emp_email, acc_name, acc_number, ifsc_code, emp_password, 'Pending', oth_emp_id_value, 'Payroll Processing System')
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
        cursor.execute("SELECT * FROM Employee WHERE emp_email = %s", (emp_email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['emp_password'], emp_password):
            session['user_id'] = user['emp_id']
            if user['emp_designation'] == 'Admin':  # Assuming designation 'Admin' for admin users
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html', flask_secret_key=os.environ.get('FLASK_SECRET_KEY'))

# Function to get all employees for admin panel
def get_all_employees():
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT emp_id, f_name, m_name, l_name, emp_email, verification_status
        FROM Employee
    """)

    employees = cursor.fetchall()
    connection.close()

    return employees

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['user_id'] == 1:  # Replace '1' with the ID of your admin user
        employees = get_all_employees()
        return render_template('admin_dashboard.html', employees=employees)
    else:
        return redirect(url_for('login'))

# Route to update employee verification status from admin panel
@app.route('/admin_update_verification/<int:emp_id>', methods=['POST'])
def admin_update_verification(emp_id):
    if 'user_id' in session and session['user_id'] == 1:
        if request.method == 'POST':
            verification_status = request.form['verification_status']

            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Employee
                SET verification_status = %s
                WHERE emp_id = %s
            """, (verification_status, emp_id))

            connection.commit()
            cursor.close()
            connection.close()

            flash('Employee verification status updated successfully.')
            return redirect(url_for('admin_dashboard'))

    return redirect(url_for('login'))

#FUNCTION FOR DASHBORD PAGE
@app.route('/dashboard') 
def dashboard():
    if 'user_id' in session:
        connection = get_mysql_connection(app)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Employee WHERE emp_id = %s", (session['user_id'],))
        employee = cursor.fetchone()
        connection.close()
        if employee:
            #employer_logo_url = employee.get('employer_logo_url', '')
            return render_template('dashboard.html', employee=employee) #, employer_logo_url=employer_logo_url)
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
    app.run(debug=True)
