"""
Dataset Integrity Verification Suite
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DATA_DIR = "c:/Users/Gokul/OneDrive/文档/hcl/data"

def test_datasets_exist_and_valid():
    required_files = {
        "careers.csv": ["career_id", "career_title", "description"],
        "skills.csv": ["skill_id", "skill_name", "category"],
        "career_skills.csv": ["id", "career_id", "skill_id", "required_level", "importance"],
        "courses.csv": ["course_id", "title", "skill_id", "difficulty", "prerequisites", "duration_hours"],
        "projects.csv": ["project_id", "title", "skill_id", "difficulty"],
        "assessments.csv": ["assessment_id", "skill_id", "question", "correct_answer"],
        "learning_history.csv": ["history_id", "user_id", "course_id", "status"]
    }

    for filename, required_cols in required_files.items():
        filepath = os.path.join(DATA_DIR, filename)
        assert os.path.exists(filepath), f"Missing dataset file: {filepath}"
        
        df = pd.read_csv(filepath)
        assert len(df) > 0, f"Dataset file is empty: {filename}"
        
        for col in required_cols:
            assert col in df.columns, f"Missing column '{col}' in {filename}"
        
        print(f"Verified dataset '{filename}': {len(df)} records.")

if __name__ == "__main__":
    test_datasets_exist_and_valid()
