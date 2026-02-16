from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if session.get('admin_logged_in'):
        return render_template('admin.html')
    return redirect(url_for('admin_login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Admin login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('admin.html')

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/a_dashboard')
def a_dashboard():
    return render_template('a_dashboard.html')

@app.route('/add_mechanic')
def add_mechanic():
    return render_template('add_mechanic.html')


# View Customers
@app.route('/view_customers')
def view_customers():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    return render_template('view_customers.html', users=users)

# Delete Customer
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('view_customers'))

# View Mechanics
@app.route('/view_mechanics')
def view_mechanics():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mechanics")
        mechanics = cursor.fetchall()
    return render_template('view_mechanic.html', mechanics=mechanics)

# Delete Mechanic
@app.route('/delete_mechanic/<int:mech_id>', methods=['POST'])
def delete_mechanic(mech_id):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mechanics WHERE id = ?", (mech_id,))
        conn.commit()
    flash("Mechanic deleted successfully!", "success")
    return redirect(url_for('view_mechanics'))

# Mechanic Register (Admin Adding Mechanic)
@app.route('/mechanic_registers', methods=['POST'])
def mechanic_registers():
    fname = request.form['fname']
    lname = request.form['lname']
    address = request.form['address']
    skill = request.form['skill']
    mobile = request.form['mobile']
    animal = request.form['animal']
    password = request.form['password']
    document = request.files['document']

    fname = request.form['fname']
    lname = request.form['lname']
    address = request.form['address']
    skill = request.form['skill']
    mobile = request.form['mobile']
    animal = request.form['animal']
    password = request.form['password']
    document = request.files['document']

    if document and allowed_file(document.filename):
        filename = document.filename
        document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = None

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mechanics (fname, lname, address, skill, mobile, animal, password, document)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (fname, lname, address, skill, mobile, animal, password, filename))
            conn.commit()
            flash('Mechanic registration successful!', 'success')
            return redirect(url_for('a_dashboard'))
        except sqlite3.IntegrityError:
            flash('Mobile number already registered.', 'error')
            return redirect(url_for('add_mechanic'))
#feedback
@app.route('/feedback')
def feedback():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contact")
        feedback = cursor.fetchall()
    return render_template('feedback.html', contact=feedback)

@app.route('/log')
def log():
    session.clear()
    return redirect(url_for('index'))

#show request in Admin
def get_request_history(user_id):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.location, r.vehicle_type, r.complaint, m.fname, m.lname,u.fname, r.status
            FROM requests r
            JOIN mechanics m ON r.mechanic_id = m.id
            JOIN users u ON r.user_id=u.id
        """)
        requests = cursor.fetchall()
    return requests
@app.route('/admin_show_req')
def admin_show_req():
    user_id = session.get('user_id')
    requests = get_request_history(user_id)
    return render_template('admin_show_req.html', requests=requests)

#admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        # Total mechanics
        cursor.execute("SELECT COUNT(*) FROM mechanics")
        total_mechanics = cursor.fetchone()[0]
    return render_template('a_dashboard.html', 
                           total_users=total_users, 
                           total_mechanics=total_mechanics)



if __name__ == '__main__':
    app.run(debug=True)