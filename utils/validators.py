"""
Validation helper module for checking application data integrity and user inputs.
"""

from typing import Tuple, List, Dict, Any
from utils.constants import SUPPORTED_CAREERS, SKILL_LEVELS


def validate_skill_level(level: int) -> Tuple[bool, str]:
    """Validate if skill level is an integer between 0 and 5."""
    if not isinstance(level, int):
        return False, "Skill level must be an integer."
    if level < 0 or level > 5:
        return False, "Skill level must be between 0 (No Knowledge) and 5 (Expert)."
    return True, "Valid"


def validate_study_hours(hours: float) -> Tuple[bool, str]:
    """Validate weekly available study hours."""
    if not isinstance(hours, (int, float)):
        return False, "Study hours must be a number."
    if hours <= 0:
        return False, "Study hours must be greater than 0."
    if hours > 80:
        return False, "Study hours cannot exceed 80 hours per week."
    return True, "Valid"


def validate_career_goal(career: str) -> Tuple[bool, str]:
    """Validate target career goal selection."""
    if not career or not isinstance(career, str):
        return False, "Career goal cannot be empty."
    if career not in SUPPORTED_CAREERS:
        return False, f"Career '{career}' is not currently supported. Choose from: {', '.join(SUPPORTED_CAREERS)}"
    return True, "Valid"
