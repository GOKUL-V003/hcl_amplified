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


def get_persisted_gemini_key() -> str:
    """Retrieve saved Gemini API key from runtime environment or .env file."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            os.environ["GEMINI_API_KEY"] = val
                            return val
        except Exception:
            pass
    return ""


def save_persisted_gemini_key(key: str) -> None:
    """Save Gemini API key to runtime environment and .env file for persistence."""
    clean_key = (key or "").strip()
    os.environ["GEMINI_API_KEY"] = clean_key
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    try:
        lines = []
        key_found = False
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines):
                if line.strip().startswith("GEMINI_API_KEY="):
                    lines[idx] = f"GEMINI_API_KEY={clean_key}\n"
                    key_found = True
                    break
        if not key_found:
            lines.append(f"\nGEMINI_API_KEY={clean_key}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception as e:
        print(f"[save_persisted_gemini_key] Error writing to .env: {e}")


def delete_persisted_gemini_key() -> None:
    """Permanently erase Gemini API key from runtime environment and .env file."""
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    save_persisted_gemini_key("")
