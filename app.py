from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

# Helper function to get db connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="AN56@pari",
        database="companydb"
    )

# Login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        db.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials. Please try admin / admin123."
            
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employee")
    employees = cursor.fetchall()
    db.close()
    return render_template("index.html", employees=employees, username=session.get('username'))

@app.route("/add_employee", methods=["POST"])
@login_required
def add_employee():
    emp_id = request.form["emp_id"]
    emp_name = request.form["emp_name"]
    age = request.form["age"]
    city = request.form["city"]
    dept_id = request.form["dept_id"]
    salary = request.form["salary"]
    hire_date = request.form["hire_date"]
    gender = request.form["gender"]

    db = get_db()
    cursor = db.cursor()
    sql = """
    INSERT INTO employee 
    (emp_id, emp_name, age, city, dept_id, salary, hire_date, gender)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    values = (emp_id, emp_name, age, city, dept_id, salary, hire_date, gender)
    try:
        cursor.execute(sql, values)
        db.commit()
    except Exception as e:
        print(f"Error adding employee: {e}")
    finally:
        db.close()

    return redirect(url_for('home'))

@app.route("/edit_employee/<id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == "POST":
        emp_name = request.form["emp_name"]
        age = request.form["age"]
        city = request.form["city"]
        dept_id = request.form["dept_id"]
        salary = request.form["salary"]
        hire_date = request.form["hire_date"]
        gender = request.form["gender"]
        
        sql = """
        UPDATE employee 
        SET emp_name=%s, age=%s, city=%s, dept_id=%s, salary=%s, hire_date=%s, gender=%s
        WHERE emp_id=%s
        """
        values = (emp_name, age, city, dept_id, salary, hire_date, gender, id)
        cursor.execute(sql, values)
        db.commit()
        db.close()
        return redirect(url_for('home'))
        
    cursor.execute("SELECT * FROM employee WHERE emp_id=%s", (id,))
    employee = cursor.fetchone()
    db.close()
    return render_template("edit_employee.html", emp=employee)

@app.route("/delete_employee/<id>", methods=["GET"])
@login_required
def delete_employee(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM employee WHERE emp_id=%s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('home'))

@app.route("/salary/<id>")
@login_required
def salary_slip(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employee WHERE emp_id=%s", (id,))
    emp = cursor.fetchone()
    db.close()
    
    if emp:
        base = float(emp['salary'])
        hra = base * 0.20
        da = base * 0.10
        gross = base + hra + da
        tax = gross * 0.05
        net = gross - tax
        
        salary_details = {
            'base': round(base, 2),
            'hra': round(hra, 2),
            'da': round(da, 2),
            'gross': round(gross, 2),
            'tax': round(tax, 2),
            'net': round(net, 2),
            'month': datetime.datetime.now().strftime("%B %Y")
        }
        return render_template("salary.html", emp=emp, salary=salary_details)
    return redirect(url_for('home'))

@app.route("/leaves")
@login_required
def leave_management():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT l.*, e.emp_name FROM leaves l JOIN employee e ON l.emp_id = e.emp_id")
    leaves = cursor.fetchall()
    
    cursor.execute("SELECT emp_id, emp_name FROM employee")
    employees = cursor.fetchall()
    db.close()
    return render_template("leaves.html", leaves=leaves, employees=employees)

@app.route("/apply_leave", methods=["POST"])
@login_required
def apply_leave():
    emp_id = request.form["emp_id"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    reason = request.form["reason"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO leaves (emp_id, start_date, end_date, reason) VALUES (%s, %s, %s, %s)",
                   (emp_id, start_date, end_date, reason))
    db.commit()
    db.close()
    return redirect(url_for('leave_management'))

@app.route("/update_leave/<id>/<status>")
@login_required
def update_leave(id, status):
    if status in ['Approved', 'Rejected']:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE leaves SET status=%s WHERE leave_id=%s", (status, id))
        db.commit()
        db.close()
    return redirect(url_for('leave_management'))


if __name__ == "__main__":
    app.run(debug=True)
    
  
    