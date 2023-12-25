from database import get_mysql_connection, create_all_tables
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv
import os
from data_fetch import fetch_all_data
from datetime import datetime
load_dotenv()  # Load environment variables from .env file
app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'a_secure_random_key_here'
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Psatpsat')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'payroll_processing_system')
# Ensure database tables are created when the app starts
with app.app_context():
    create_all_tables(app)

#FUNCTION FOR INDEX PAGE
@app.route('/')
def index():
    return render_template('index.html')

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
    # Check if the user is already logged in
    elif 'user_id' in session:
        if session['user_id'] == 1:  # Replace '1' with the ID of your admin user
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    return render_template('login.html') #, flask_secret_key=os.environ.get('FLASK_SECRET_KEY'))

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['user_id'] == 1:  # Replace '1' with the ID of your admin user
        all_data = fetch_all_data(app)
        return render_template('admin_dashboard.html', employees=all_data['employee_data'],attendance_data=all_data['attendance_data'] ,leave_data=all_data['leave_data'],salary_data=all_data['salary_data'],employer_data=all_data['employer_data'])
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

@app.route('/add_new_employee', methods=['GET', 'POST'])
def add_new_employee():
    if 'user_id' not in session or session['user_id'] != 1:
        abort(403)

    if request.method == 'POST':
        try:
            # Retrieve form data
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
            emp_ver_id = request.form['emp_ver_id']
            oth_emp_id_value = request.form['oth_emp_id']
            emp_password = generate_password_hash(request.form['emp_password'], method='pbkdf2:sha1')
            # Convert the 'emp_dob' date string to the correct format
            dob_datetime = datetime.strptime(emp_dob, '%d-%m-%Y')
            formatted_dob = dob_datetime.strftime('%Y-%m-%d')
            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            # cursor.execute("SELECT emp_id FROM Employee WHERE emp_ver_id = %s", (emp_ver_id,))
            # emp_id_values = cursor.fetchone()
            # emp_id = emp_id_values[0]
            # Check if there is an existing record for the emp_ver_id
            cursor.execute("SELECT * FROM Employee WHERE emp_ver_id = %s", (emp_ver_id,))
            existing_record = cursor.fetchone()
            if existing_record:
                # Update the existing record
                cursor.execute("""
                    UPDATE Employee
                    SET f_name = %s,
                        m_name = %s,
                        l_name = %s,
                        emp_designation = %s,
                        emp_dob = %s,
                        emp_mobile_no = %s,
                        emp_email = %s,
                        acc_name = %s,
                        acc_number = %s,
                        ifsc_code = %s,
                        emp_ver_id = %s,
                        emp_password = %s,
                        oth_emp_id = %s
                    WHERE emp_id = %s
                """, (f_name, m_name, l_name, emp_designation, formatted_dob, emp_mobile_no, emp_email, acc_name, acc_number, ifsc_code, emp_ver_id, emp_password, oth_emp_id_value, emp_id))
            else:
                # Insert a new record
                cursor.execute("""
                    INSERT INTO Employee (f_name, m_name, l_name, emp_designation, emp_dob, emp_mobile_no, emp_email, acc_name, acc_number, ifsc_code, emp_ver_id, emp_password, verification_status, oth_emp_id, employer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (f_name, m_name, l_name, emp_designation, formatted_dob, emp_mobile_no, emp_email, acc_name, acc_number, ifsc_code, emp_ver_id, emp_password, 'Pending', oth_emp_id_value, 'Payroll Processing System'))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'An error occurred while adding a new employee: {e}')
            return redirect(url_for('error_page'))
    else:
        all_data=fetch_all_data(app)
        return render_template('add_new_employee.html', employees=all_data['employee_data'])


@app.route('/update_attendance', methods=['GET', 'POST'])
def update_attendance():
    if 'user_id' not in session or session['user_id'] != 1:
        abort(403)
    try:
        if request.method == 'POST':
            # Retrieve form data
            emp_id = request.form.get('emp_id')
            present_days = request.form.get('present_days')
            absent_days = request.form.get('absent_days')
            connection = get_mysql_connection(app)
            cursor = connection.cursor()
            # Check if there is an existing record for the emp_id
            cursor.execute("SELECT * FROM Attendance WHERE emp_id = %s", (emp_id,))
            existing_record = cursor.fetchone()
            if existing_record:
                # Update the existing record
                cursor.execute("""
                    UPDATE Attendance
                    SET present_days = %s,
                    absent_days = %s
                    WHERE emp_id = %s
                """, (present_days, absent_days, emp_id))
            else:
                print(emp_id)
                # Insert the values provided in the HTML form
                cursor.execute("""
                    INSERT INTO Attendance (emp_id, present_days, absent_days)
                    VALUES (%s, %s, %s)
                """, (emp_id, present_days, absent_days))
            connection.commit()
            cursor.close()
            connection.close()            
            # Redirect to the admin dashboard or another appropriate page
            return redirect(url_for('admin_dashboard'))
        else:
            # Handle other cases or redirect to an error page
            return redirect(url_for('error_page'))
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")    
    # This line will be reached even if an exception occurs
    all_data=fetch_all_data(app)
    return render_template('update_attendance.html', employees=all_data['employee_data'])

@app.route('/update_leave', methods=['GET', 'POST'])
def update_leave():
    try:
        if 'user_id' not in session or session['user_id'] != 1:
            abort(403)
        if request.method == 'POST':
            # Retrieve form data
            emp_id = request.form.get('emp_id')
            leave_type = request.form.get('leave_type')
            number_of_days = request.form.get('number_of_days')

            connection = get_mysql_connection(app)
            cursor = connection.cursor()

            # Check if there is an existing record for the emp_id
            cursor.execute("SELECT * FROM `Leave` WHERE emp_id = %s", (emp_id,))
            existing_record = cursor.fetchone()

            if existing_record:
                # Update the existing record
                cursor.execute("""
                    UPDATE `Leave`
                    SET leave_type = %s,
                    number_of_days = %s
                    WHERE emp_id = %s
                """, (leave_type, number_of_days, emp_id))
            else:
                # Insert a new record for the emp_id
                cursor.execute("""
                    INSERT INTO `Leave` (emp_id, leave_type, number_of_days)
                    VALUES (%s, %s, %s)
                """, (emp_id, leave_type, number_of_days))

            connection.commit()
            cursor.close()
            connection.close()            
            # Redirect to the admin dashboard or another appropriate page
            return redirect(url_for('admin_dashboard'))
        else:
            # Handle other cases or redirect to an error page
            return redirect(url_for('error_page'))
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")
    all_data=fetch_all_data(app)
    return render_template('update_leave.html', employees=all_data['employee_data'])

@app.route('/add_new_employer', methods=['GET', 'POST'])
def add_new_employer():
    try:
        if 'user_id' not in session or session['user_id'] != 1:
            abort(403)
        if request.method == 'POST':
            # Retrieve form data
            emp_id = request.form.get('emp_id')
            empl_desg = request.form.get('empl_desg')
            empl_mob_no = request.form.get('empl_mob_no')
            empl_depart = request.form.get('empl_depart')
            
            connection = get_mysql_connection(app)
            cursor = connection.cursor(dictionary=True)

            # Check if there is an existing record for the emp_id in the Employee table
            cursor.execute("SELECT * FROM Employee WHERE emp_id = %s", (emp_id,))
            existing_employee_record = cursor.fetchone()
            empl_id=existing_employee_record.get('oth_emp_id','0')
            if existing_employee_record:
                # Fetch the empl_id from the Employer table for the given empl_id
                cursor.execute("SELECT * FROM Employer WHERE empl_id = %s", (empl_id,))
                existing_employer_record = cursor.fetchone()

                if existing_employer_record:
                    # Update the existing record in the Employer table
                    cursor.execute("""
                        UPDATE Employer
                        SET empl_desg = %s,
                            empl_mob_no = %s,
                            empl_depart = %s 
                        WHERE empl_id = %s
                    """, (empl_desg, empl_mob_no, empl_depart, empl_id))
                else:
                    # Insert a new record in the Employer table
                    cursor.execute("""
                        INSERT INTO Employer (empl_desg, empl_mob_no, empl_depart)
                        VALUES (%s, %s, %s)
                    """, (empl_desg, empl_mob_no, empl_depart))

                connection.commit()
                cursor.close()
                connection.close()
                # Redirect to the admin dashboard or another appropriate page
                return redirect(url_for('admin_dashboard'))

            else:
                # Handle the case where no existing record is found in the Employee table
                return redirect(url_for('error_page'))

        else:
            # Handle other cases or redirect to an error page
            return redirect(url_for('error_page'))

    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")
    
    all_data=fetch_all_data(app)
    return render_template('add_new_employer.html', employees=all_data['employee_data'])

@app.route('/prepare_monthly_salary', methods=['GET', 'POST'])
def prepare_monthly_salary():
    try:
        if 'user_id' not in session or session['user_id'] != 1:
            abort(403)
        if request.method == 'POST':
            # Retrieve form data
            emp_id = request.form.get('emp_id')
            empl_id = request.form.get('empl_id')
            # Retrieve other form data for salary components
            hra = float(request.form.get('hra', 0))
            da = float(request.form.get('da', 0))
            ba = float(request.form.get('ba', 0))
            ta = float(request.form.get('ta', 0))
            incentive = float(request.form.get('incentive', 0))
            # Calculate total salary
            total_salary = hra + da + ba + ta + incentive
            # Calculate salary based on attendance and leave data
            salary = calculate_salary(emp_id, total_salary)

            connection = get_mysql_connection(app)
            cursor = connection.cursor(dictionary=True)

            # Check if there is an existing record for the emp_id in the SalaryCalculation table
            cursor.execute("SELECT * FROM SalaryCalculation WHERE emp_id = %s", (emp_id,))
            existing_salary_record = cursor.fetchone()

            # Fetch the empl_id and oth_emp_id from the Employee table for the given emp_id
            cursor.execute("SELECT * FROM Employee WHERE emp_id = %s", (emp_id,))
            employee_data = cursor.fetchone()
            if employee_data:
                if existing_salary_record:
                    # Update the existing record in the SalaryCalculation table
                    cursor.execute("""
                        UPDATE SalaryCalculation
                        SET empl_id = %s
                            hra = %s,
                            da = %s,
                            ba = %s,
                            ta = %s,
                            incentive = %s,
                            total_salary = %s
                            net_salary = %s
                        WHERE emp_id = %s
                    """, (empl_id, hra, da, ba, ta, incentive, total_salary,salary, emp_id))
                else:
                    # Insert a new record in the SalaryCalculation table
                    cursor.execute("""
                        INSERT INTO SalaryCalculation (emp_id, empl_id, hra, da, ba, ta, incentive, total_salary,net_salary)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (emp_id, empl_id, hra, da, ba, ta, incentive, total_salary,salary))

                connection.commit()
                cursor.close()
                connection.close()
                # Redirect to the admin dashboard or another appropriate page
                return redirect(url_for('admin_dashboard'))

            else:
                # Handle the case where no existing record is found in the Employee table
                return redirect(url_for('error_page'))

        else:
            # Handle other cases or redirect to an error page
            return redirect(url_for('error_page'))

    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")

    all_data=fetch_all_data(app)
    return render_template('prepare_monthly_salary.html', employees=all_data['employee_data'])

def calculate_salary(emp_id, total_salary):
    connection = get_mysql_connection(app)
    cursor = connection.cursor(dictionary=True)
    # Fetch attendance data for the employee
    cursor.execute("SELECT * FROM Attendance WHERE emp_id = %s", (emp_id,))
    attendance_data = cursor.fetchone()
    present_days = attendance_data.get('present_days', 0)
    # Fetch leave data for the employee
    cursor.execute("SELECT * FROM `Leave` WHERE emp_id = %s", (emp_id,))
    leave_data = cursor.fetchone()
    leave_days = leave_data.get('number_of_days', 0)
    # Deduction rate (replace with your actual deduction rate)
    deduction_rate = 100
    # Total working days
    total_days = 30  # Assuming a month with 30 days
    total_working_days = total_days - attendance_data.get('absent_days', 0)
    # Calculate daily rate
    daily_rate = total_salary / total_working_days
    # Calculate earnings
    earnings = daily_rate * present_days
    # Calculate deductions
    deductions = deduction_rate * leave_days
    # Calculate net salary
    net_salary = earnings - deductions
    cursor.close()
    connection.close()
    return net_salary

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
            # Check if the user is an admin (you can adjust this condition based on your roles)
            if employee.get('emp_designation') == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
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