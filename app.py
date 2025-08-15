from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Database Setup ---
def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect('pypath.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the required tables."""
    with app.app_context():
        conn = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        
        # Add a default admin user
        cursor = conn.cursor()
        # Check if admin already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        admin_user = cursor.fetchone()
        if not admin_user:
            hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)', 
                           ('admin', hashed_password, 1))

        conn.commit()
        conn.close()

# --- User Authentication ---
@app.route('/')
def index():
    """Renders the main landing page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            flash('Username already exists!', 'danger')
            conn.close()
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user from the database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.clear()
    return redirect(url_for('index'))

# --- Application Logic ---
@app.route('/dashboard')
def dashboard():
    """Displays the user's dashboard."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html')

@app.route('/quiz')
def quiz():
    """Displays the initial skills benchmark quiz."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()
    return render_template('quiz.html', questions=questions)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Processes the quiz submission and calculates the score."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    score = 0
    conn = get_db_connection()
    questions = conn.execute('SELECT id, correct_answer FROM questions').fetchall()
    
    for question in questions:
        user_answer = request.form.get(f'question_{question["id"]}')
        if user_answer == question['correct_answer']:
            score += 1

    # Store the result
    conn.execute('INSERT INTO results (user_id, score) VALUES (?, ?)', (session['user_id'], score))
    conn.commit()
    conn.close()

    return redirect(url_for('results'))

@app.route('/results')
def results():
    """Displays the user's quiz results and learning analytics."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    result = conn.execute('SELECT * FROM results WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', 
                          (session['user_id'],)).fetchone()
    total_questions = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    conn.close()

    if not result:
        flash('You have not taken any quizzes yet.', 'info')
        return redirect(url_for('dashboard'))

    # Simple adaptive logic
    learning_modules = []
    if result['score'] / total_questions < 0.5:
        learning_modules.append("Learning Module 1: Python Basics")
    else:
        learning_modules.append("Learning Module 5: Advanced Python")

    return render_template('results.html', result=result, total_questions=total_questions, learning_modules=learning_modules)

# --- Admin Section ---
@app.route('/admin')
def admin_dashboard():
    """Displays the admin dashboard with all student results."""
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Join users and results tables to get student names and their scores
    all_results = conn.execute('''
        SELECT u.username, r.score, r.timestamp 
        FROM results r
        JOIN users u ON u.id = r.user_id
        ORDER BY r.timestamp DESC
    ''').fetchall()
    
    total_questions = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    conn.close()
    
    return render_template('admin.html', all_results=all_results, total_questions=total_questions)


if __name__ == '__main__':
    if not os.path.exists('pypath.db'):
        init_db()
    app.run(debug=True)
