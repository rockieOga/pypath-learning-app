-- schema.sql

-- Drop tables if they exist to ensure a clean slate
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS results;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);

-- Questions table for the quizzes
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL
);

-- Sample Questions (can be expanded)
INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_answer) VALUES
('What is the output of `print(2 ** 3)`?', '6', '8', '9', '12', 'B'),
('Which of the following is a mutable type in Python?', 'string', 'tuple', 'list', 'integer', 'C'),
('How do you start a single-line comment in Python?', '//', '#', '/*', '<!--', 'B'),
('What does the `len()` function do?', 'Returns the length of an object', 'Returns the largest value', 'Converts to lowercase', 'Returns a random number', 'A'),
('Which keyword is used to define a function in Python?', 'def', 'function', 'fun', 'define', 'A');


-- Results table to store quiz outcomes
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
