from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import bcrypt
import io
import json
import uuid
from contextlib import redirect_stdout

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- W3Schools Topic URL Mapping ---
W3SCHOOLS_LINKS = {
    "Operators": "https://www.w3schools.com/python/python_operators.asp",
    "Data Types": "https://www.w3schools.com/python/python_datatypes.asp",
    "Syntax": "https://www.w3schools.com/python/python_syntax.asp",
    "Built-in Functions": "https://www.w3schools.com/python/python_ref_functions.asp",
    "Functions": "https://www.w3schools.com/python/python_functions.asp",
    "Strings": "https://www.w3schools.com/python/python_strings.asp",
    "Loops": "https://www.w3schools.com/python/python_for_loops.asp"
}


# --- Database Setup ---
def get_db_connection():
    conn = sqlite3.connect('pypath.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            hashed_password = bcrypt.hashpw('rockieOga'.encode('utf-8'), bcrypt.gensalt())
            student_code = str(uuid.uuid4())
            cursor.execute('INSERT INTO users (username, password, student_code, first_name, last_name, is_admin) VALUES (?, ?, ?, ?, ?, ?)', 
                           ('admin', hashed_password, student_code, 'Admin', 'User', 1))
        conn.commit()
        conn.close()

# --- Helper Functions ---
def get_user_id():
    return session.get('user_id')

def is_admin():
    return session.get('is_admin', False)

# --- Authentication & Profile Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        
        conn = get_db_connection()
        if conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone():
            flash('Username already exists.', 'danger')
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            student_code = str(uuid.uuid4())
            conn.execute('INSERT INTO users (username, password, student_code, first_name, last_name, middle_name) VALUES (?, ?, ?, ?, ?, ?)',
                         (username, hashed_password, student_code, first_name, last_name, middle_name))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        conn.close()
    return render_template('register.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not get_user_id(): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form['middle_name']
        
        conn.execute('UPDATE users SET first_name = ?, last_name = ?, middle_name = ? WHERE id = ?',
                     (first_name, last_name, middle_name, get_user_id()))
        conn.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
        
    user = conn.execute('SELECT * FROM users WHERE id = ?', (get_user_id(),)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

# --- Other backend routes from previous version remain here ---
# (login, logout, dashboard, admin routes, quiz routes, etc.)
# For brevity, I am not repeating all the unchanged code.
# The full app.py file would include all previous routes.

# --- Placeholder for the rest of the app.py code ---
@app.route('/')
def index():
    if get_user_id(): return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'], session['username'], session['is_admin'] = user['id'], user['username'], bool(user['is_admin'])
            session['first_name'] = user['first_name']
            return redirect(url_for('dashboard'))
        else: flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not get_user_id(): return redirect(url_for('login'))
    conn = get_db_connection()
    if is_admin():
        # Admin dashboard logic...
        return render_template('admin/dashboard.html') # Simplified for brevity
    else:
        # Student dashboard logic...
        return render_template('student/dashboard.html') # Simplified for brevity

@app.route('/admin/history')
def student_history():
    if not is_admin(): return redirect(url_for('login'))
    # Student history logic...
    return render_template('admin/history.html') # Simplified for brevity
