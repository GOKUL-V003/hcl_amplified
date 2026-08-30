"""
Database Layer Integration Unit Tests
"""

import os
import sys
import tempfile
# pyrefly: ignore [missing-import]
import pytest

# Ensure root workspace directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Fixture providing a clean test DatabaseManager instance per test."""
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_learning.db")

    db = DatabaseManager(db_path=test_db_path)
    yield db


def test_schema_and_seeding(db_manager):
    """Verify that tables are created and seeded properly from CSV files."""
    careers = db_manager.get_careers()
    assert len(careers) >= 5
    assert careers[0]["career_title"] == "Data Analyst"

    skills = db_manager.get_skills()
    assert len(skills) >= 15

    courses = db_manager.get_all_courses()
    assert len(courses) >= 50

    projects = db_manager.get_all_projects()
    assert len(projects) >= 15


def test_user_profile_crud(db_manager):
    """Test user profile creation, retrieval, and updating."""
    user_id = db_manager.create_user("Alice Tech", 2, "Machine Learning, Python", 15.0)
    assert user_id > 0

    user = db_manager.get_user(user_id)
    assert user is not None
    assert user["name"] == "Alice Tech"
    assert user["career_title"] == "Data Scientist"

    # Update profile
    success = db_manager.update_user(user_id, "Alice Advanced", 3, "Deep Learning", 20.0)
    assert success is True

    updated_user = db_manager.get_user(user_id)
    assert updated_user["name"] == "Alice Advanced"
    assert updated_user["career_title"] == "AI/ML Engineer"


def test_user_skills_matrix(db_manager):
    """Test setting and getting user skill levels."""
    user_id = db_manager.create_user("Bob Learner", 1, "Data", 10.0)

    db_manager.set_user_skill(user_id, 1, 3)  # Excel = 3
    db_manager.set_user_skill(user_id, 2, 1)  # SQL = 1
    db_manager.set_user_skill(user_id, 3, 2)  # Python = 2

    user_skills = db_manager.get_user_skills(user_id)
    assert user_skills[1] == 3
    assert user_skills[2] == 1
    assert user_skills[3] == 2

    # Test update existing skill
    db_manager.set_user_skill(user_id, 2, 3)  # SQL updated from 1 to 3
    updated_skills = db_manager.get_user_skills(user_id)
    assert updated_skills[2] == 3


def test_learning_history_recording(db_manager):
    """Test logging course completions."""
    user_id = db_manager.create_user("Charlie", 1, "SQL", 5.0)

    db_manager.record_course_status(user_id, 5, "Completed")  # Course 5 = SQL Basics
    history = db_manager.get_user_learning_history(user_id)

    assert len(history) == 1
    assert history[0]["course_id"] == 5
    assert history[0]["status"] == "Completed"
    assert history[0]["title"] == "SQL Basics: Querying Relational Databases"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
