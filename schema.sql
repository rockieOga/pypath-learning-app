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
    profile_image TEXT, -- Base64 image data
    is_admin INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0
);

-- Questions table: The central bank for all questions
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

-- Student Topic Mastery table
CREATE TABLE student_topic_mastery (
    user_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, topic),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Achievements tables
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

-- Question Sets table
CREATE TABLE question_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT
);

-- Set_Questions table
CREATE TABLE set_questions (
    set_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    PRIMARY KEY (set_id, question_id),
    FOREIGN KEY (set_id) REFERENCES question_sets (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- Results table
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

-- Student_Answers table
CREATE TABLE student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES results (id),
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

-- Recommendations table
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_text TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- --- PRE-POPULATED DATA ---

-- Expanded Question Bank
INSERT INTO questions (question_text, question_type, topic, option_a, option_b, option_c, option_d, correct_answer) VALUES
('What is the output of `print(2 ** 3)`?', 'multiple_choice', 'Operators', '6', '8', '9', '12', 'B'),
('Which of the following is a mutable type in Python?', 'multiple_choice', 'Data Types', 'string', 'tuple', 'list', 'integer', 'C'),
('How do you start a single-line comment in Python?', 'multiple_choice', 'Syntax', '//', '#', '/*', '<!--', 'B'),
('What does the `len()` function do?', 'multiple_choice', 'Built-in Functions', 'Returns the length of an object', 'Returns the largest value', 'Converts to lowercase', 'Returns a random number', 'A'),
('Which keyword is used to define a function in Python?', 'multiple_choice', 'Functions', 'def', 'function', 'fun', 'define', 'A'),
('What will `print("hello"[1:3])` output?', 'multiple_choice', 'Strings', 'hel', 'ell', 'he', 'el', 'D'),
('Which loop is best for iterating over a list of items?', 'multiple_choice', 'Loops', 'while loop', 'for loop', 'if statement', 'do-while loop', 'B'),
('How do you assign the value `5` to a variable named `x`?', 'multiple_choice', 'Syntax', 'x = 5', 'x == 5', 'let x = 5', 'x := 5', 'A'),
('What is the result of ` "Py" + "Path" `?', 'multiple_choice', 'Strings', 'Py Path', 'PyPath', 'Error', 'Py+Path', 'B'),
('How do you get the first item from a list named `my_list`?', 'multiple_choice', 'Data Types', 'my_list(0)', 'my_list[0]', 'my_list.first()', 'my_list.get(0)', 'B'),
('Which of the following creates a dictionary?', 'multiple_choice', 'Data Types', '`["name": "John"]`', '`("name", "John")`', '`{"name": "John"}`', '`<name: "John">`', 'C'),
('What is the comparison operator for "not equal to"?', 'multiple_choice', 'Operators', '!=', '<>', '=/=', '!==', 'A');

-- Coding Questions
INSERT INTO questions (question_type, topic, question_text, correct_code_output) VALUES
('coding', 'Syntax', 'Write a single line of Python code that prints the string "Hello, World!".', 'Hello, World!\n'),
('coding', 'Functions', 'Write a Python function named `add_two` that takes two numbers as arguments and returns their sum. Then call the function with 5 and 3 and print the result.', '8\n');

-- Create a default question set
INSERT INTO question_sets (title, description) VALUES
('Python Fundamentals Quiz', 'A basic quiz covering the fundamentals of Python programming.');

-- Add all questions to the default set
INSERT INTO set_questions (set_id, question_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (1, 14);

-- Add achievements
INSERT INTO achievements (name, description, icon) VALUES
('First Steps', 'Complete your first quiz.', 'check-circle'),
('Perfect Score', 'Get 100% on any quiz.', 'shield-question');
