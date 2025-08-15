-- schema.sql

-- Drop tables in reverse order of dependency to avoid foreign key constraints
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS student_answers;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS set_questions;
DROP TABLE IF EXISTS question_sets;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS users;


-- Users table: Stores user credentials and roles
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    student_code TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0
);

-- Questions table: The central bank for all questions
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL DEFAULT 'multiple_choice', -- 'multiple_choice' or 'coding'
    topic TEXT NOT NULL, -- e.g., 'Variables', 'Loops', 'Functions' for the recommender system
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT,
    correct_code_output TEXT
);

-- Question Sets table: Allows admin to group questions into quizzes
CREATE TABLE question_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT
);

-- Set_Questions table: Links questions to question sets (many-to-many relationship)
CREATE TABLE set_questions (
    set_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    PRIMARY KEY (set_id, question_id),
    FOREIGN KEY (set_id) REFERENCES question_sets (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- Results table: Stores high-level results for each quiz attempt
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    set_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (set_id) REFERENCES question_sets (id)
);

-- Student_Answers table: Stores the student's specific answer for each question for detailed analysis
CREATE TABLE student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct INTEGER NOT NULL, -- 1 for true, 0 for false
    FOREIGN KEY (result_id) REFERENCES results (id),
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

-- Recommendations table: Stores personalized recommendations for students
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- --- PRE-POPULATED DATA ---

-- Add some topics to the question bank
INSERT INTO questions (question_text, question_type, topic, option_a, option_b, option_c, option_d, correct_answer) VALUES
('What is the output of `print(2 ** 3)`?', 'multiple_choice', 'Operators', '6', '8', '9', '12', 'B'),
('Which of the following is a mutable type in Python?', 'multiple_choice', 'Data Types', 'string', 'tuple', 'list', 'integer', 'C'),
('How do you start a single-line comment in Python?', 'multiple_choice', 'Syntax', '//', '#', '/*', '<!--', 'B'),
('What does the `len()` function do?', 'multiple_choice', 'Built-in Functions', 'Returns the length of an object', 'Returns the largest value', 'Converts to lowercase', 'Returns a random number', 'A'),
('Which keyword is used to define a function in Python?', 'multiple_choice', 'Functions', 'def', 'function', 'fun', 'define', 'A'),
('What will `print("hello"[1:3])` output?', 'multiple_choice', 'Strings', 'hel', 'ell', 'he', 'el', 'D'),
('Which loop is best for iterating over a list of items?', 'multiple_choice', 'Loops', 'while loop', 'for loop', 'if statement', 'do-while loop', 'B');

-- Add coding questions
INSERT INTO questions (question_type, topic, question_text, correct_code_output) VALUES
('coding', 'Syntax', 'Write a single line of Python code that prints the string "Hello, World!".', 'Hello, World!\n'),
('coding', 'Functions', 'Write a Python function named `add_two` that takes two numbers as arguments and returns their sum. Then call the function with 5 and 3 and print the result.', '8\n');

-- Create a default question set
INSERT INTO question_sets (title, description) VALUES
('Python Fundamentals Quiz', 'A basic quiz covering the fundamentals of Python programming.');

-- Add all questions to the default set
INSERT INTO set_questions (set_id, question_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9);
