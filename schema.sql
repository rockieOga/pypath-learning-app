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
    question_type TEXT NOT NULL DEFAULT 'multiple_choice', -- 'multiple_choice' or 'coding'
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT, -- For multiple choice
    correct_code_output TEXT -- For coding questions
);

-- Sample Questions (can be expanded)
INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_answer) VALUES
('What is the output of `print(2 ** 3)`?', '6', '8', '9', '12', 'B'),
('Which of the following is a mutable type in Python?', 'string', 'tuple', 'list', 'integer', 'C'),
('How do you start a single-line comment in Python?', '//', '#', '/*', '<!--', 'B'),
('What does the `len()` function do?', 'Returns the length of an object', 'Returns the largest value', 'Converts to lowercase', 'Returns a random number', 'A'),
('Which keyword is used to define a function in Python?', 'def', 'function', 'fun', 'define', 'A'),
('What is the correct way to create a list in Python?', '`[1, 2, 3]`', '`(1, 2, 3)`', '`{1, 2, 3}`', '`list(1, 2, 3)`', 'A'),
('What will `print("hello"[1:3])` output?', 'hel', 'ell', 'he', 'el', 'D'),
('Which of these is NOT a Python data type?', 'Integer', 'Float', 'String', 'Character', 'D');


-- Coding Questions
INSERT INTO questions (question_type, question_text, correct_code_output) VALUES
('coding', 'Write a single line of Python code that prints the string "Hello, World!".', 'Hello, World!\n'),
('coding', 'Write a Python function named `add_two` that takes two numbers as arguments and returns their sum. Then call the function with the numbers 5 and 3 and print the result.', '8\n');


-- Results table to store quiz outcomes
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
