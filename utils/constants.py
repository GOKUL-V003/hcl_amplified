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

# Sample Career Analyzer Prompts for Quick Testing
SAMPLE_CAREER_PROMPTS = {
    "Data Analyst": "I am an entry-level graduate with a business background looking to transition into a Data Analyst role. I know basic Excel formulas and have done simple SQL queries, but I have zero experience with Python, Pandas, and statistics. I can dedicate about 12 hours a week to study.",
    "Data Scientist": "I want to become a professional Data Scientist. I have intermediate programming skills in Python and good foundational statistics, but need to master Machine Learning pipelines, Pandas optimization, and predictive modeling. I have 15 hours per week available.",
    "AI/ML Engineer": "I am working as a software developer and want to transition to an AI/ML Engineer. I am proficient in Python, Git, and basic ML algorithms, but I need deep learning, PyTorch, and NLP transformers. I can commit 14 hours each week.",
    "Web Developer": "I am a self-taught beginner aiming to become a Web Developer. I know basic HTML and CSS, but struggle with JavaScript ES6 and React state management. I can study 10 hours a week.",
    "Cybersecurity Specialist": "I want to switch to a Cybersecurity Analyst position. I have strong computer networking and TCP/IP knowledge, but need hands-on ethical hacking, Wireshark packet analysis, and OWASP vulnerability auditing skills. I can invest 12 hours a week."
}
