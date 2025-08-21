-- schema.sql

-- Drop tables in reverse order of dependency
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS student_answers;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS set_questions;
DROP TABLE IF EXISTS question_sets;
DROP TABLE IF EXISTS student_topic_mastery;
DROP TABLE IF EXISTS student_achievements;
DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS users;


-- Users table with gamification and profile image fields
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    student_code TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    profile_image TEXT, -- New column for base64 image data
    is_admin INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0
);

-- Questions table (unchanged)
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL DEFAULT 'multiple_choice',
    topic TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT,
    correct_code_output TEXT
);

-- New table to track topic-specific progress
CREATE TABLE student_topic_mastery (
    user_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, topic),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- New tables for achievements
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL
);

CREATE TABLE student_achievements (
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (achievement_id) REFERENCES achievements (id)
);


-- Other tables (unchanged)
CREATE TABLE question_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT
);

CREATE TABLE set_questions (
    set_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    PRIMARY KEY (set_id, question_id),
    FOREIGN KEY (set_id) REFERENCES question_sets (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    set_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    time_start DATETIME NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (set_id) REFERENCES question_sets (id)
);

CREATE TABLE student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES results (id),
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- --- PRE-POPULATED DATA ---
INSERT INTO questions (question_text, question_type, topic, option_a, option_b, option_c, option_d, correct_answer) VALUES
('What is the output of `print(2 ** 3)`?', 'multiple_choice', 'Operators', '6', '8', '9', '12', 'B'),
('Which of the following is a mutable type in Python?', 'multiple_choice', 'Data Types', 'string', 'tuple', 'list', 'integer', 'C');
INSERT INTO question_sets (title, description) VALUES ('Python Fundamentals Quiz', 'A basic quiz covering the fundamentals of Python programming.');
INSERT INTO set_questions (set_id, question_id) VALUES (1, 1), (1, 2);
INSERT INTO achievements (name, description, icon) VALUES ('First Steps', 'Complete your first quiz.', 'check-circle'), ('Perfect Score', 'Get 100% on any quiz.', 'shield-question');
