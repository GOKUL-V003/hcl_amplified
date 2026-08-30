"""
AI Career Analyzer Service Unit & Integration Tests
"""

import os
import sys
import tempfile
# pyrefly: ignore [missing-import]
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ai_analyzer import CareerAnalyzerService
from database.database import DatabaseManager
from utils.constants import SAMPLE_CAREER_PROMPTS, SUPPORTED_CAREERS


@pytest.fixture
def analyzer():
    return CareerAnalyzerService()


@pytest.fixture
def test_db():
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_analyzer.db")
    db = DatabaseManager(db_path=test_db_path)
    yield db


from unittest.mock import patch

def test_missing_api_key_raises_error(analyzer):
    """Verify that analyzing without an API key raises an informative error directing to Google AI Studio."""
    with pytest.raises(ValueError, match="Google Gemini API Key is required"):
        analyzer.analyze_career_prompt("I want to be a Web Developer", custom_api_key="")


def test_gemini_api_analysis_success(analyzer):
    """Verify that a successful Gemini API call properly returns the structured learner profile."""
    mock_gemini_response = {
        "target_career": "Web Developer",
        "experience_level": "Beginner",
        "study_hours_per_week": 12.0,
        "interests": "Web Development, HTML & CSS, Python",
        "career_summary": "Aspiring Web Developer with foundational skills in Python and HTML.",
        "learning_strategy": "Focus on modern JavaScript and React state management.",
        "detected_skills": {
            "Excel": 0, "SQL": 0, "Python": 2, "Pandas": 0, "Statistics": 0,
            "Data Visualization": 0, "Power BI": 0, "Machine Learning": 0,
            "Deep Learning": 0, "HTML & CSS": 2, "JavaScript": 0, "React": 0,
            "Network Security": 0, "Ethical Hacking": 0, "Git": 0
        }
    }

    with patch.object(analyzer, "_call_gemini_api", return_value=mock_gemini_response):
        profile = analyzer.analyze_career_prompt("i know python,html", custom_api_key="AIzaSy_fake_test_key")
        assert profile["target_career"] == "Web Developer"
        assert profile["detected_skills"]["Python"] == 2
        assert profile["detected_skills"]["HTML & CSS"] == 2
        assert profile["source"] == "Google Gemini 1.5 Flash (Live AI)"


def test_empty_prompt_fallback(analyzer):
    """Verify graceful handling when user input is empty."""
    profile = analyzer.analyze_career_prompt("")
    assert profile["target_career"] in SUPPORTED_CAREERS
    assert profile["study_hours_per_week"] > 0


def test_course_explanation_generation(analyzer, test_db):
    """Verify dynamic recommendation rationale generation."""
    user_skills = {1: 0, 2: 1, 3: 2} # Excel=0, SQL=1, Python=2
    career_reqs = test_db.get_career_skills(1) # Data Analyst
    courses = test_db.get_all_courses()

    # Excel course (gap from 0 to target)
    excel_course = next((c for c in courses if c["skill_name"] == "Excel"), courses[0])
    rationale = analyzer.generate_course_explanation(excel_course, user_skills, career_reqs)
    
    assert "Excel" in rationale
    assert len(rationale) > 20


def test_curriculum_strategy_generation(analyzer, test_db):
    """Verify high-level curriculum strategy generation."""
    import pandas as pd
    df_skills = pd.DataFrame([
        {"Skill": "Python", "Gap": 2, "Importance": 0.9},
        {"Skill": "SQL", "Gap": 1, "Importance": 0.8}
    ])
    strategy = analyzer.generate_curriculum_strategy("Data Analyst", df_skills, 12.0)
    assert "Data Analyst" in strategy
    assert "Python" in strategy


def test_profile_sync_to_database(analyzer, test_db):
    """Verify that an AI-detected profile updates SQLite user and skill tables."""
    mock_gemini_profile = {
        "target_career": "Data Analyst",
        "experience_level": "Beginner",
        "study_hours_per_week": 12.0,
        "interests": "Data Analysis, Excel, SQL",
        "career_summary": "Aspiring Data Analyst with foundational background.",
        "learning_strategy": "Master Excel formulas and SQL queries.",
        "detected_skills": {"Excel": 3, "SQL": 2, "Python": 0}
    }

    with patch.object(analyzer, "_call_gemini_api", return_value=mock_gemini_profile):
        profile = analyzer.analyze_career_prompt("I want to be a Data Analyst", custom_api_key="AIzaSy_fake_test_key")

    careers = test_db.get_careers()
    career_map = {c["career_title"]: c["career_id"] for c in careers}
    career_id = career_map.get(profile["target_career"], 1)

    user_id = test_db.create_user("AI Test User", career_id, profile["interests"], profile["study_hours_per_week"])
    assert user_id > 0

    skills = test_db.get_skills()
    skill_map = {s["skill_name"]: s["skill_id"] for s in skills}

    for skill_name, level in profile["detected_skills"].items():
        if skill_name in skill_map:
            test_db.set_user_skill(user_id, skill_map[skill_name], level)

    user = test_db.get_user(user_id)
    assert user["career_title"] == "Data Analyst"
    assert user["study_hours_per_week"] == 12.0

    synced_skills = test_db.get_user_skills(user_id)
    excel_id = skill_map.get("Excel")
    if excel_id:
        assert synced_skills[excel_id] >= 2


def test_generate_diagnostic_quiz(analyzer):
    """Verify dynamic diagnostic quiz generation for target skills."""
    skills = ["HTML & CSS", "JavaScript", "React"]
    quiz = analyzer.generate_diagnostic_quiz("Web Developer", skills, "Beginner with HTML knowledge")
    
    assert len(quiz) >= 3
    for q in quiz:
        assert "id" in q
        assert "skill" in q
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) == 4
        assert "correct_index" in q
        assert 0 <= q["correct_index"] < 4


def test_evaluate_diagnostic_quiz(analyzer):
    """Verify objective scoring and verified skill level calculation from diagnostic answers."""
    sample_quiz = [
        {
            "id": 1,
            "skill": "JavaScript",
            "question": "What is typeof null?",
            "options": ["A) null", "B) object", "C) undefined", "D) boolean"],
            "correct_index": 1,
            "target_level": 3
        },
        {
            "id": 2,
            "skill": "HTML & CSS",
            "question": "Which is 2D layout?",
            "options": ["A) CSS Grid", "B) Flexbox", "C) Float", "D) Inline"],
            "correct_index": 0,
            "target_level": 3
        }
    ]

    # User answers Q1 correctly (index 1), Q2 incorrectly (index 1 instead of 0)
    user_answers = {1: 1, 2: 1}
    eval_result = analyzer.evaluate_diagnostic_quiz(sample_quiz, user_answers)

    assert eval_result["total_questions"] == 2
    assert eval_result["correct_count"] == 1
    assert eval_result["score_pct"] == 50.0
    assert eval_result["verified_skills"]["JavaScript"] == 3  # Passed -> Level 3
    assert eval_result["verified_skills"]["HTML & CSS"] == 1  # Failed -> Gap identified (Level 1)
    assert eval_result["skill_evaluations"]["JavaScript"]["is_correct"] is True
    assert eval_result["skill_evaluations"]["HTML & CSS"]["is_correct"] is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])
