from flask import Flask, render_template, request, redirect, url_for, session, flash # type: ignore
import sqlite3
import os
from werkzeug.utils import secure_filename # type: ignore


app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                animal TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mechanics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fname TEXT NOT NULL,
                lname TEXT NOT NULL,
                address TEXT NOT NULL,
                skill TEXT NOT NULL,
                mobile TEXT NOT NULL UNIQUE,
                animal TEXT NOT NULL,
                password TEXT NOT NULL,
                document TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    mechanic_id INTEGER,
    location TEXT,
    vehicle_type TEXT,
    complaint TEXT,
    status TEXT DEFAULT 'Pending'
);

        """)
        cursor.execute(""" CREATE TABLE IF NOT EXISTS contact(name TEXT,
                       email TEXT,
                       mobile INTEGER,
                       message TEXT);""")
    print("Database initialized.")


init_db()

# Routes

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/About')
def About():
    return render_template('About.html')

@app.route('/mechanic')
def mechanic():
    return render_template('mechanic.html')

@app.route('/m_dashboard')
def m_dashboard():
    return render_template('m_dashboard.html')

@app.route('/mecreg')
def mecreg():
    return render_template('mecreg.html')

@app.route('/meclogin')
def meclogin():
    return render_template('meclogin.html')

@app.route('/customer_dashboard')
def c_dashboard():
    return render_template('c_dashboard.html')

@app.route('/c_reset')
def c_reset():
    return render_template('c_reset.html')
@app.route('/logt')
def logt():
    return render_template('meclogin.html')
@app.route('/add_mechanic')
def add_mechanic():
    return render_template('add_mechanic.html')

@app.route('/select_mechanic')
def select_mechanic():
    return render_template('request_service.html')
#contact
@app.route('/con', methods=['POST'])
def con():
    name = request.form['name']
    email = request.form['email']
    mobile=request.form['phone']
    message=request.form['message']
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contact (name, email, mobile, message)
            VALUES (?, ?, ?, ?)
        """, (name, email, mobile, message))
        conn.commit()
        flash('Feedback submited successful!', 'success')
        return redirect(url_for('contact'))


# Mechanic Registration (Self)
@app.route('/mechanic_register', methods=['POST'])
def mechanic_register():
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
            return redirect(url_for('meclogin'))
        except sqlite3.IntegrityError:
            flash('Mobile number already registered.', 'Error')
            return redirect(url_for('mecreg'))

# Mechanic Login
@app.route('/mechanic_login', methods=['POST'])
def mechanic_login():
    session.clear()
    mobile = request.form['mobile']
    password = request.form['password']

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mechanics WHERE mobile = ? AND password = ?", (mobile, password))
        user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        session['user_mobile'] = user[5]
        flash('Login successful!', 'success')
        return redirect(url_for('m_dashboard'))
    else:
        flash('Invalid credentials.', 'error')
        
        return redirect(url_for('meclogin'))

# Mechanic Password Reset
@app.route('/m_reset', methods=['GET', 'POST'])
def m_reset():
    
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        animal = request.form.get('animal')

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mechanics WHERE mobile = ? AND animal = ?", (mobile, animal))
            user = cursor.fetchone()

        if user:
            session['reset_mobile'] = mobile
            return redirect(url_for('show_mpass_form'))
        else:
            flash('Invalid details.', 'error')
            return redirect(url_for('m_reset'))
    return render_template('m_reset.html')

@app.route('/mpass_up', methods=['GET', 'POST'])
def show_mpass_form():
    if request.method == 'POST':
        new_password = request.form.get('password')
        mobile = session.get('reset_mobile')

        if mobile and new_password:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE mechanics SET password = ? WHERE mobile = ?", (new_password, mobile))
                conn.commit()

            flash('Password updated.', 'success')
            session.pop('reset_mobile', None)
            return redirect(url_for('meclogin'))
        else:
            flash('Session expired or missing data.', 'error')
            return redirect(url_for('m_reset'))
    
    return render_template('mpass_up.html')

# Customer Registration
@app.route('/register', methods=['POST'])
def register():
    fname = request.form['fname']
    lname = request.form['lname']
    animal = request.form['animal']
    email = request.form['email']
    password = request.form['password']

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (fname, lname, animal, email, password)
                VALUES (?, ?, ?, ?, ?)
            """, (fname, lname, animal, email, password))
            conn.commit()
            flash('Registration successful.', 'success')
            return redirect(url_for('customer'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'error')
            return redirect(url_for('customer'))

# Customer Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        flash('Login successful!', 'Success')
        return redirect(url_for('c_dashboard'))
    else:
        flash('Invalid credentials.', 'Error')
        return redirect(url_for('customer'))

# Customer Reset
@app.route('/reset', methods=['POST'])
def reset():
    email = request.form.get('email')
    animal = request.form.get('animal')

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND animal = ?", (email, animal))
        user = cursor.fetchone()

    if user:
        session['reset_email'] = email
        return redirect(url_for('show_cpass_form'))
    else:
        flash('Invalid details.', 'error')
        return redirect(url_for('c_reset'))

@app.route('/cpass_up', methods=['GET', 'POST'])
def show_cpass_form():
    if request.method == 'POST':
        new_password = request.form.get('password')
        email = session.get('reset_email')

        if email and new_password:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
                conn.commit()

            flash('Password updated.', 'success')
            session.pop('reset_email', None)
            return redirect(url_for('customer'))
        else:
            flash('Session expired or missing data.', 'error')
            return redirect(url_for('c_reset'))
    
    return render_template('cpass_up.html')

#user profile
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to view your profile.', 'error')
        return redirect(url_for('customer'))

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fname, lname, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

    if user:
        return render_template('profile.html', user=user)
    else:
        flash('User not found.', 'error')
        return redirect(url_for('customer'))

#mechanic profile
@app.route('/mechanic_profile')
def mechanic_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to view your profile.', 'error')
        return redirect(url_for('meclogin'))

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fname, lname, address, skill, mobile, animal, document 
            FROM mechanics 
            WHERE id = ?
        """, (user_id,))
        mechanic = cursor.fetchone()

    if mechanic:
        return render_template('mechanic_profile.html', mechanic=mechanic)
    else:
        flash('Mechanic not found.', 'error')
        return redirect(url_for('meclogin'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('customer'))

@app.route('/back')
def back():
    session.clear()
    return redirect(url_for('mechanic'))

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/request_service', methods=['GET', 'POST'])
def request_service():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, fname, lname FROM mechanics")
    mechanics = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        mechanic_id = request.form.get('mechanic')
        if not mechanic_id:
            return "Please select a mechanic", 400
        # Process the selected mechanic (save service request etc.)
        return "Service request submitted!"

    return render_template('request_service.html', mechanics=mechanics)

#edit mechanic profile
@app.route('/edit_mechanic_profile', methods=['GET', 'POST'])
def edit_mechanic_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to edit profile.', 'error')
        return redirect(url_for('meclogin'))

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            address = request.form['address']
            skill = request.form['skill']

            document_filename = None
            file = request.files['document']

            if file and allowed_file(file.filename):
                document_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))
                cursor.execute("""
                    UPDATE mechanics
                    SET fname = ?, lname = ?, address = ?, skill = ?, document = ?
                    WHERE id = ?
                """, (fname, lname, address, skill, document_filename, user_id))
            else:
                cursor.execute("""
                    UPDATE mechanics
                    SET fname = ?, lname = ?, address = ?, skill = ?
                    WHERE id = ?
                """, (fname, lname, address, skill, user_id))

            conn.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('mechanic_profile'))

        cursor.execute("SELECT fname, lname, address, skill FROM mechanics WHERE id = ?", (user_id,))
        mechanic = cursor.fetchone()

    return render_template('edit_mechanic_profile.html', mechanic=mechanic)


#user request

def get_mechanics():
    conn = sqlite3.connect('users.db')  # Use your actual DB name
    cursor = conn.cursor()
    cursor.execute("SELECT id, fname, lname, address FROM mechanics")
    mechanics = cursor.fetchall()
    conn.close()
    return mechanics

@app.route('/mechanics')
def show_mechanics():
    mechanics = get_mechanics()
    return render_template('aaa.html', mechanics=mechanics)


@app.route('/submit_selection', methods=['POST'])
def submit_selection():
    selected_id = request.form['mechanic']
    # You can fetch and show more mechanic details using this ID if needed
    return f"You selected mechanic with ID: {selected_id}"

@app.route('/selec_mechanic')
def selec_mechanic():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fname, lname, address FROM mechanics")
        mechanics = cursor.fetchall()
    return render_template('aaa.html', mechanics=mechanics)

@app.route('/submi_selection', methods=['POST'])
def submi_selection():
    mechanic_id = request.form['mechanic']
    location = request.form['location']
    vehicle_type = request.form['vehicle_type']
    complaint = request.form['complaint']

    # Assuming user_id is stored in session after login
    user_id = session.get('user_id')
    if not user_id:
        return "User not logged in", 401

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO requests (user_id, mechanic_id, location, vehicle_type, complaint)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, mechanic_id, location, vehicle_type, complaint))
        conn.commit()

    return redirect('/customer_dashboard')  # or some confirmation page


#request histroy
def get_request_history(user_id):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.location, r.vehicle_type, r.complaint, m.fname, m.lname, r.status,m.mobile
            FROM requests r
            JOIN mechanics m ON r.mechanic_id = m.id
            WHERE r.user_id = ?
        """, (user_id,))
        requests = cursor.fetchall()
    return requests
@app.route('/request_history')
def request_history():
    user_id = session.get('user_id')
    if not user_id:
        return "User  not logged in", 401

    requests = get_request_history(user_id)
    return render_template('request_history.html', requests=requests)

#mechanics request history
@app.route('/incoming_requests')
def incoming_requests():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please login to view requests.', 'error')
        return redirect(url_for('meclogin'))

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.location, r.vehicle_type, r.complaint, u.fname, u.lname, r.status
            FROM requests r
            JOIN users u ON r.user_id = u.id
            WHERE r.mechanic_id = ?
        """, (user_id,))
        requests = cursor.fetchall()

    return render_template('incoming_requests.html', requests=requests)
@app.route('/update_request_status/<int:request_id>/<string:new_status>', methods=['POST'])
def update_request_status(request_id, new_status):
    if new_status not in ['Accepted', 'Rejected']:
        return "Invalid status", 400

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET status = ? WHERE id = ?", (new_status, request_id))
        conn.commit()

    flash(f"Request status updated to {new_status}", "success")
    return redirect(url_for('incoming_requests'))






if __name__ == '__main__':
    app.run(debug=True)