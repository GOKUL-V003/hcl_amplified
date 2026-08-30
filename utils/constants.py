"""
System Constants and Configuration Defaults
"""

# Skill Level Mapping (0-5 Scale)
SKILL_LEVELS = {
    0: "No Knowledge",
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced",
    5: "Expert"
}

SKILL_LEVEL_NAMES = {v: k for k, v in SKILL_LEVELS.items()}

# Skill Gap Priority Levels
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"
PRIORITY_COMPLETE = "Complete"

# Recommendation Scoring Weights (Rule-Based component)
DEFAULT_RECOMMENDATION_WEIGHTS = {
    "skill_gap": 0.30,
    "goal_relevance": 0.25,
    "prerequisite_match": 0.15,
    "difficulty_match": 0.10,
    "interest_match": 0.10,
    "resource_quality": 0.10,
}

# Hybrid Score Blending (Rule vs ML)
HYBRID_RULE_WEIGHT = 0.60
HYBRID_ML_WEIGHT = 0.40

# Supported Careers
CAREER_DATA_ANALYST = "Data Analyst"
CAREER_DATA_SCIENTIST = "Data Scientist"
CAREER_AIML_ENGINEER = "AI/ML Engineer"
CAREER_WEB_DEVELOPER = "Web Developer"
CAREER_CYBERSECURITY_ANALYST = "Cybersecurity Analyst"

SUPPORTED_CAREERS = [
    CAREER_DATA_ANALYST,
    CAREER_DATA_SCIENTIST,
    CAREER_AIML_ENGINEER,
    CAREER_WEB_DEVELOPER,
    CAREER_CYBERSECURITY_ANALYST,
]

# Database Path
DEFAULT_DB_PATH = "database/learning_recommender.db"
