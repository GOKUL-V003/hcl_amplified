"""
Utility and helper functions for data manipulation, formatting, and validation.
"""

import os
import json
from typing import Dict, Any, List, Optional
from utils.constants import SKILL_LEVELS


def get_skill_level_label(level: int) -> str:
    """Return descriptive text label for numeric skill level (0-5)."""
    return SKILL_LEVELS.get(level, f"Unknown ({level})")


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format float value (0.0 - 1.0 or 0-100) as percentage string."""
    if value <= 1.0 and value >= 0.0:
        return f"{value * 100:.{decimals}f}%"
    return f"{value:.{decimals}f}%"


def parse_json_safely(data_str: Optional[str], default: Any = None) -> Any:
    """Safely parse JSON string, returning default on failure."""
    if default is None:
        default = []
    if not data_str:
        return default
    try:
        return json.loads(data_str)
    except (json.JSONDecodeError, TypeError):
        return default


def ensure_directory_exists(file_path: str) -> None:
    """Ensure parent directory of a target file path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
