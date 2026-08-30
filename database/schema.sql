-- Database Schema for AI-Powered Personalized Learning Path Recommender

PRAGMA foreign_keys = ON;

-- 1. Careers Table
CREATE TABLE IF NOT EXISTS careers (
    career_id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_title TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 2. Skills Table
CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
);

-- 3. Career Skills Mapping (Requirement Matrix)
CREATE TABLE IF NOT EXISTS career_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    required_level INTEGER NOT NULL CHECK (required_level BETWEEN 0 AND 5),
    importance REAL NOT NULL CHECK (importance BETWEEN 0.0 AND 1.0),
    FOREIGN KEY (career_id) REFERENCES careers(career_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 4. Learning Resources (Courses) Table
CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    skill_id INTEGER NOT NULL,
    difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    prerequisites TEXT, -- JSON array string, e.g. "[1, 5]"
    duration_hours REAL NOT NULL DEFAULT 1.0,
    resource_type TEXT NOT NULL, -- Course, Video, Tutorial, Documentation, Project, Quiz
    provider TEXT NOT NULL,
    url TEXT,
    rating REAL DEFAULT 4.5,
    tags TEXT,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 5. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    skill_id INTEGER NOT NULL,
    difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    estimated_hours REAL DEFAULT 10.0,
    tags TEXT,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 6. Assessments Table
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    difficulty INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 7. Users Profile Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    career_goal_id INTEGER,
    interests TEXT,
    experience_level TEXT DEFAULT 'Beginner',
    study_hours_per_week REAL DEFAULT 10.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (career_goal_id) REFERENCES careers(career_id) ON DELETE SET NULL
);

-- 8. User Skills Matrix Table
CREATE TABLE IF NOT EXISTS user_skills (
    user_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    current_level INTEGER NOT NULL DEFAULT 0 CHECK (current_level BETWEEN 0 AND 5),
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

-- 9. User Learning History Table
CREATE TABLE IF NOT EXISTS learning_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Completed', 'In Progress', 'Skipped')),
    completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 10. User Feedback Table
CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    feedback_type TEXT NOT NULL, -- Useful, Too Easy, Too Difficult, Already Know This
    rating_score INTEGER CHECK (rating_score BETWEEN 1 AND 5),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);
