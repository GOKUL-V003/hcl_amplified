"""
Database Manager for SQLite operations, schema initialization, CSV seeding, and CRUD queries.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from utils.helpers import ensure_directory_exists, parse_json_safely
from utils.constants import DEFAULT_DB_PATH


class DatabaseManager:
    """Manages SQLite database initialization, CSV seeding, and CRUD operations."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        ensure_directory_exists(self.db_path)
        self.schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a new SQLite database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Initialize database tables using schema.sql and seed from CSV files if empty."""
        with self.get_connection() as conn:
            if os.path.exists(self.schema_path):
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()

        # Seed data if tables are empty
        self.seed_data_from_csv()

    def seed_data_from_csv(self, data_dir: Optional[str] = None) -> None:
        """Populate database tables from CSV files if they are empty."""
        if data_dir is None:
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Seed Careers
            cursor.execute("SELECT COUNT(*) FROM careers")
            if cursor.fetchone()[0] == 0:
                careers_file = os.path.join(data_dir, "careers.csv")
                if os.path.exists(careers_file):
                    df = pd.read_csv(careers_file)
                    df.to_sql("careers", conn, if_exists="append", index=False)

            # Seed Skills
            cursor.execute("SELECT COUNT(*) FROM skills")
            if cursor.fetchone()[0] == 0:
                skills_file = os.path.join(data_dir, "skills.csv")
                if os.path.exists(skills_file):
                    df = pd.read_csv(skills_file)
                    df.to_sql("skills", conn, if_exists="append", index=False)

            # Seed Career Skills Requirement Matrix
            cursor.execute("SELECT COUNT(*) FROM career_skills")
            if cursor.fetchone()[0] == 0:
                cs_file = os.path.join(data_dir, "career_skills.csv")
                if os.path.exists(cs_file):
                    df = pd.read_csv(cs_file)
                    df.to_sql("career_skills", conn, if_exists="append", index=False)

            # Seed Courses
            cursor.execute("SELECT COUNT(*) FROM courses")
            if cursor.fetchone()[0] == 0:
                courses_file = os.path.join(data_dir, "courses.csv")
                if os.path.exists(courses_file):
                    df = pd.read_csv(courses_file)
                    df.to_sql("courses", conn, if_exists="append", index=False)

            # Seed Projects
            cursor.execute("SELECT COUNT(*) FROM projects")
            if cursor.fetchone()[0] == 0:
                projects_file = os.path.join(data_dir, "projects.csv")
                if os.path.exists(projects_file):
                    df = pd.read_csv(projects_file)
                    df.to_sql("projects", conn, if_exists="append", index=False)

            # Seed Assessments (Ensure full 225 questions bank)
            cursor.execute("SELECT COUNT(*) FROM assessments")
            if cursor.fetchone()[0] < 225:
                cursor.execute("DELETE FROM assessments")
                assessments_file = os.path.join(data_dir, "assessments.csv")
                if os.path.exists(assessments_file):
                    df = pd.read_csv(assessments_file)
                    df.to_sql("assessments", conn, if_exists="append", index=False)

            conn.commit()

        # Create default demo user if zero users exist
        self._ensure_default_user()

    def _ensure_default_user(self) -> int:
        """Create a default user record if none exists."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """INSERT INTO users (name, career_goal_id, interests, study_hours_per_week)
                       VALUES (?, ?, ?, ?)""",
                    ("Yash", 1, "Data Analysis, Python, SQL, Machine Learning", 12.0)
                )
                user_id = cursor.lastrowid
                # Seed initial skills for Yash (Excel=3, Python=2, SQL=1)
                cursor.execute("INSERT OR REPLACE INTO user_skills (user_id, skill_id, current_level) VALUES (?, ?, ?)", (user_id, 1, 3))
                cursor.execute("INSERT OR REPLACE INTO user_skills (user_id, skill_id, current_level) VALUES (?, ?, ?)", (user_id, 3, 2))
                cursor.execute("INSERT OR REPLACE INTO user_skills (user_id, skill_id, current_level) VALUES (?, ?, ?)", (user_id, 2, 1))
                conn.commit()
                return user_id
            cursor.execute("SELECT user_id FROM users LIMIT 1")
            return cursor.fetchone()[0]

    # --- User Profile CRUD ---
    def create_user(self, name: str, career_goal_id: int, interests: str = "", study_hours: float = 10.0) -> int:
        """Insert new user profile and return user_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, career_goal_id, interests, study_hours_per_week) VALUES (?, ?, ?, ?)",
                (name, career_goal_id, interests, study_hours)
            )
            conn.commit()
            return cursor.lastrowid

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user profile record by user_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT u.*, c.career_title 
                   FROM users u 
                   LEFT JOIN careers c ON u.career_goal_id = c.career_id 
                   WHERE u.user_id = ?""",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user(self, user_id: int, name: str, career_goal_id: int, interests: str, study_hours: float) -> bool:
        """Update existing user profile fields."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE users 
                   SET name = ?, career_goal_id = ?, interests = ?, study_hours_per_week = ? 
                   WHERE user_id = ?""",
                (name, career_goal_id, interests, study_hours, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # --- User Skills CRUD ---
    def set_user_skill(self, user_id: int, skill_id: int, level: int) -> None:
        """Upsert a skill level for a specific user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO user_skills (user_id, skill_id, current_level)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id, skill_id) DO UPDATE SET current_level = excluded.current_level""",
                (user_id, skill_id, level)
            )
            conn.commit()

    def get_user_skills(self, user_id: int) -> Dict[int, int]:
        """Fetch dictionary mapping skill_id -> current_level for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT skill_id, current_level FROM user_skills WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return {row["skill_id"]: row["current_level"] for row in rows}

    # --- Domain Queries ---
    def get_careers(self) -> List[Dict[str, Any]]:
        """Return list of all careers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM careers ORDER BY career_id")
            return [dict(r) for r in cursor.fetchall()]

    def get_skills(self) -> List[Dict[str, Any]]:
        """Return list of all skills."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skills ORDER BY skill_id")
            return [dict(r) for r in cursor.fetchall()]

    def get_career_skills(self, career_id: int) -> List[Dict[str, Any]]:
        """Return list of skill requirements for a given career_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT cs.*, s.skill_name, s.category
                   FROM career_skills cs
                   JOIN skills s ON cs.skill_id = s.skill_id
                   WHERE cs.career_id = ?
                   ORDER BY cs.importance DESC""",
                (career_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_all_courses(self) -> List[Dict[str, Any]]:
        """Return all available learning resources (courses)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT c.*, s.skill_name 
                   FROM courses c 
                   JOIN skills s ON c.skill_id = s.skill_id"""
            )
            courses = []
            for r in cursor.fetchall():
                c = dict(r)
                c["prerequisites"] = parse_json_safely(c.get("prerequisites"), [])
                courses.append(c)
            return courses

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Return all capstone projects."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.*, s.skill_name 
                   FROM projects p 
                   JOIN skills s ON p.skill_id = s.skill_id"""
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_assessments_for_skill(self, skill_id: int) -> List[Dict[str, Any]]:
        """Return assessment questions for a specific skill."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM assessments WHERE skill_id = ? ORDER BY difficulty ASC",
                (skill_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    # --- History & Feedback ---
    def record_course_status(self, user_id: int, course_id: int, status: str = "Completed") -> None:
        """Log or update course progress for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO learning_history (user_id, course_id, status)
                   VALUES (?, ?, ?)""",
                (user_id, course_id, status)
            )
            conn.commit()

    def get_user_learning_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch full learning history logs for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT lh.*, c.title, c.url, c.skill_id, s.skill_name
                   FROM learning_history lh
                   JOIN courses c ON lh.course_id = c.course_id
                   JOIN skills s ON c.skill_id = s.skill_id
                   WHERE lh.user_id = ?
                   ORDER BY lh.completion_date DESC""",
                (user_id,)
            )
            return [dict(r) for r in cursor.fetchall()]

    def delete_learning_history_item(self, history_id: int) -> None:
        """Delete a single history log entry by history_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM learning_history WHERE history_id = ?", (history_id,))
            conn.commit()

    def clear_user_learning_history(self, user_id: int) -> None:
        """Delete all learning history records for a specific user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM learning_history WHERE user_id = ?", (user_id,))
            conn.commit()
