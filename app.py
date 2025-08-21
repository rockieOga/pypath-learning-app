from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import bcrypt
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Gamification Constants ---
XP_PER_CORRECT_ANSWER = 10
XP_TO_LEVEL_UP = 100

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
    conn = sqlite3.connect('pypath.db', check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
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

def format_duration(start_time, end_time):
    if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        return "N/A"
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0: return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0: return f"{minutes}m {seconds}s"
    return f"{seconds}s"

def calculate_proficiency(user_id, conn):
    last_result = conn.execute('SELECT id FROM results WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', (user_id,)).fetchone()
    if not last_result: return None
    answers = conn.execute('SELECT q.topic, sa.is_correct FROM student_answers sa JOIN questions q ON sa.question_id = q.id WHERE sa.result_id = ?', (last_result['id'],)).fetchall()
    topic_scores = {}
    for answer in answers:
        topic = answer['topic']
        if topic not in topic_scores: topic_scores[topic] = {'correct': 0, 'total': 0}
        topic_scores[topic]['total'] += 1
        if answer['is_correct']: topic_scores[topic]['correct'] += 1
    proficiency_analysis = []
    for topic, scores in topic_scores.items():
        percentage = (scores['correct'] / scores['total']) * 100 if scores['total'] > 0 else 0
        level, color = get_proficiency_level(percentage)
        proficiency_analysis.append({'topic': topic, 'percentage': round(percentage), 'level': level, 'color': color, 'study_link': W3SCHOOLS_LINKS.get(topic, '#')})
    return proficiency_analysis
    
def get_proficiency_level(percentage):
    if percentage >= 85: return "Proficient", "text-green-600"
    elif percentage >= 60: return "Intermediate", "text-yellow-600"
    else: return "Beginner", "text-red-600"

# --- Main Routes ---
@app.route('/')
def index():
    if get_user_id(): return redirect(url_for('dashboard'))
    return render_template('index.html')

# --- Authentication & Profile Routes ---
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form.get('middle_name')

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not get_user_id(): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        first_name, last_name, middle_name = request.form['first_name'], request.form['last_name'], request.form.get('middle_name')
        conn.execute('UPDATE users SET first_name = ?, last_name = ?, middle_name = ? WHERE id = ?', (first_name, last_name, middle_name, get_user_id()))
        conn.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    user = conn.execute('SELECT * FROM users WHERE id = ?', (get_user_id(),)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/update_profile_image', methods=['POST'])
def update_profile_image():
    if not get_user_id():
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'success': False, 'error': 'No image data provided'}), 400

    conn = get_db_connection()
    conn.execute('UPDATE users SET profile_image = ? WHERE id = ?', (image_data, get_user_id()))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

# --- Core Dashboard ---
@app.route('/dashboard')
def dashboard():
    if not get_user_id(): return redirect(url_for('login'))
    conn = get_db_connection()
    if is_admin():
        student_count = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0]
        quiz_count = conn.execute('SELECT COUNT(*) FROM question_sets').fetchone()[0]
        avg_score_data = conn.execute('SELECT AVG(score * 100.0 / total_questions) as avg_score FROM results').fetchone()
        avg_score = avg_score_data['avg_score'] if avg_score_data and avg_score_data['avg_score'] else 0
        
        student_performance = conn.execute('''
            SELECT u.first_name || ' ' || u.last_name as student_name, MAX(r.score * 100.0 / r.total_questions) as latest_score
            FROM results r
            JOIN users u ON r.user_id = u.id
            WHERE u.is_admin = 0
            GROUP BY u.id
            ORDER BY latest_score DESC
        ''').fetchall()

        chart_labels = [row['student_name'] for row in student_performance]
        chart_values = [row['latest_score'] for row in student_performance]
        
        conn.close()
        return render_template('admin/dashboard.html', 
                               student_count=student_count, 
                               quiz_count=quiz_count, 
                               avg_score=avg_score,
                               chart_labels=chart_labels,
                               chart_values=chart_values)
    else:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (get_user_id(),)).fetchone()
        sets = conn.execute('SELECT * FROM question_sets').fetchall()
        
        proficiency_raw = conn.execute('SELECT * FROM student_topic_mastery WHERE user_id = ?', (get_user_id(),)).fetchall()
        proficiency = []
        for topic_data in proficiency_raw:
            topic_dict = dict(topic_data)
            topic_dict['percentage'] = (topic_data['xp'] / XP_TO_LEVEL_UP) * 100
            topic_dict['study_link'] = W3SCHOOLS_LINKS.get(topic_data['topic'], '#')
            proficiency.append(topic_dict)

        user_data = dict(user)
        user_data['next_level_xp'] = XP_TO_LEVEL_UP

        conn.close()
        return render_template('student/dashboard.html', 
                               user=user_data, 
                               sets=sets, 
                               proficiency=proficiency)

# --- Admin Routes ---
@app.route('/admin/questions')
def admin_questions():
    if not is_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()
    return render_template('admin/questions.html', questions=questions)

@app.route('/admin/questions/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    if not is_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        text, topic = request.form['question_text'], request.form['topic']
        conn.execute('UPDATE questions SET question_text = ?, topic = ? WHERE id = ?', (text, topic, id))
        conn.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin_questions'))
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('admin/edit_question.html', question=question)

@app.route('/admin/history')
def student_history():
    if not is_admin(): return redirect(url_for('login'))
    conn = get_db_connection()
    
    search_query = request.args.get('search', '')
    base_query = '''
        SELECT 
            u.username, u.student_code, u.first_name, u.last_name, 
            qs.title, r.score, r.total_questions, r.time_start, r.timestamp as time_end,
            r.id as result_id,
            ROW_NUMBER() OVER(PARTITION BY r.user_id, r.set_id ORDER BY r.timestamp) as attempt_number
        FROM results r
        JOIN users u ON u.id = r.user_id
        JOIN question_sets qs ON qs.id = r.set_id
        WHERE u.is_admin = 0
    '''
    params = []
    if search_query:
        base_query += ' AND (u.username LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])
    base_query += ' ORDER BY r.timestamp DESC'
    history_raw = conn.execute(base_query, params).fetchall()
    history = []
    for row in history_raw:
        row_dict = dict(row)
        start_time = datetime.fromisoformat(row['time_start']) if isinstance(row['time_start'], str) else row['time_start']
        end_time = datetime.fromisoformat(row['time_end']) if isinstance(row['time_end'], str) else row['time_end']
        row_dict['duration'] = format_duration(start_time, end_time)
        row_dict['time_start_formatted'] = start_time.strftime('%I:%M:%S %p') if start_time else "N/A"
        row_dict['time_end_formatted'] = end_time.strftime('%I:%M:%S %p') if end_time else "N/A"
        row_dict['date_formatted'] = end_time.strftime('%Y-%m-%d') if end_time else "N/A"
        history.append(row_dict)
    conn.close()
    return render_template('admin/history.html', history=history, search_query=search_query)

# --- Student Routes ---
@app.route('/history')
def student_result_history():
    if not get_user_id() or is_admin():
        return redirect(url_for('login'))
    conn = get_db_connection()
    history_raw = conn.execute('''
        SELECT qs.title, r.score, r.total_questions, r.time_start, r.timestamp as time_end, r.id as result_id,
               ROW_NUMBER() OVER(PARTITION BY r.user_id, r.set_id ORDER BY r.timestamp) as attempt_number
        FROM results r JOIN question_sets qs ON r.set_id = qs.id
        WHERE r.user_id = ? ORDER BY r.timestamp DESC
    ''', (get_user_id(),)).fetchall()
    history = []
    for row in history_raw:
        row_dict = dict(row)
        start_time = datetime.fromisoformat(row['time_start']) if isinstance(row['time_start'], str) else row['time_start']
        end_time = datetime.fromisoformat(row['time_end']) if isinstance(row['time_end'], str) else row['time_end']
        row_dict['duration'] = format_duration(start_time, end_time)
        row_dict['time_start_formatted'] = start_time.strftime('%I:%M:%S %p') if start_time else "N/A"
        row_dict['time_end_formatted'] = end_time.strftime('%I:%M:%S %p') if end_time else "N/A"
        history.append(row_dict)
    conn.close()
    return render_template('student/history.html', history=history)
    
@app.route('/id_card/<student_code>')
def id_card(student_code):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE student_code = ?', (student_code,)).fetchone()
    
    if not user:
        return "User not found", 404

    proficiency_raw = conn.execute('SELECT * FROM student_topic_mastery WHERE user_id = ?', (user['id'],)).fetchall()
    
    proficiency = []
    for topic in proficiency_raw:
        topic_dict = dict(topic)
        topic_dict['percentage'] = (topic['xp'] / XP_TO_LEVEL_UP) * 100
        proficiency.append(topic_dict)

    conn.close()
    return render_template('student/id_card.html', user=user, proficiency=proficiency)

@app.route('/achievements')
def achievements():
    if not get_user_id() or is_admin():
        return redirect(url_for('login'))
    return render_template('student/achievements.html')

@app.route('/sandbox')
def code_sandbox():
    if not get_user_id() or is_admin():
        return redirect(url_for('login'))
    return render_template('student/sandbox.html')

@app.route('/quiz/<int:set_id>')
def quiz(set_id):
    if not get_user_id(): return redirect(url_for('login'))
    session['quiz_start_time'] = datetime.now().isoformat()
    conn = get_db_connection()
    questions = conn.execute('SELECT q.* FROM questions q JOIN set_questions sq ON q.id = sq.question_id WHERE sq.set_id = ?', (set_id,)).fetchall()
    set_info = conn.execute('SELECT * FROM question_sets WHERE id = ?', (set_id,)).fetchone()
    conn.close()
    return render_template('student/quiz.html', questions=questions, set_info=set_info)

@app.route('/submit_quiz/<int:set_id>', methods=['POST'])
def submit_quiz(set_id):
    if not get_user_id(): return redirect(url_for('login'))
    start_time_str = session.pop('quiz_start_time', datetime.now().isoformat())
    start_time = datetime.fromisoformat(start_time_str)

    conn = get_db_connection()
    questions = conn.execute('SELECT q.* FROM questions q JOIN set_questions sq ON q.id = sq.question_id WHERE sq.set_id = ?', (set_id,)).fetchall()
    
    score = 0
    total_xp_gained = 0

    result_cursor = conn.cursor()
    result_cursor.execute('INSERT INTO results (user_id, set_id, score, total_questions, time_start) VALUES (?, ?, 0, ?, ?)',
                          (get_user_id(), set_id, len(questions), start_time))
    result_id = result_cursor.lastrowid

    for q in questions:
        user_answer = request.form.get(f'question_{q["id"]}')
        is_correct = 1 if (q['question_type'] == 'multiple_choice' and user_answer == q['correct_answer']) else 0

        if is_correct:
            score += 1
            total_xp_gained += XP_PER_CORRECT_ANSWER
            
            conn.execute('''
                INSERT INTO student_topic_mastery (user_id, topic, xp) VALUES (?, ?, ?)
                ON CONFLICT(user_id, topic) DO UPDATE SET xp = xp + ?
            ''', (get_user_id(), q['topic'], XP_PER_CORRECT_ANSWER, XP_PER_CORRECT_ANSWER))

        conn.execute('INSERT INTO student_answers (result_id, question_id, user_answer, is_correct) VALUES (?, ?, ?, ?)', (result_id, q['id'], user_answer, is_correct))

    # Award "First Steps" achievement
    conn.execute('INSERT OR IGNORE INTO student_achievements (user_id, achievement_id) VALUES (?, 1)', (get_user_id(),))

    user = conn.execute('SELECT * FROM users WHERE id = ?', (get_user_id(),)).fetchone()
    new_xp = user['xp'] + total_xp_gained
    new_level = user['level']
    while new_xp >= XP_TO_LEVEL_UP:
        new_level += 1
        new_xp -= XP_TO_LEVEL_UP
    
    conn.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (new_xp, new_level, get_user_id()))
    conn.execute('UPDATE results SET score = ?, timestamp = ? WHERE id = ?', (score, datetime.now(), result_id))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('results', result_id=result_id))

@app.route('/results/<int:result_id>')
def results(result_id):
    if not get_user_id(): return redirect(url_for('login'))
    conn = get_db_connection()
    result = conn.execute('SELECT * FROM results WHERE id = ? AND user_id = ?', (result_id, get_user_id())).fetchone()
    if not result: return "Result not found or you do not have permission to view it.", 404
    
    proficiency_data = calculate_proficiency(get_user_id(), conn)
    
    return render_template('student/results.html', result=result, proficiency=proficiency_data)

if __name__ == '__main__':
    if not os.path.exists('pypath.db'):
        init_db()
    app.run(debug=True)
