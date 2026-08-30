"""
Smart Learning & Career Path Recommender System - Dynamic Light & Dark Theme Prototype
"""

import sys
import os
# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.database import DatabaseManager
from services.ai_analyzer import CareerAnalyzerService
from utils.constants import SKILL_LEVELS, SUPPORTED_CAREERS, SAMPLE_CAREER_PROMPTS
from utils.helpers import (
    get_skill_level_label, format_percentage,
    get_persisted_gemini_key, save_persisted_gemini_key, delete_persisted_gemini_key
)

# --- Page Configuration ---
st.set_page_config(
    page_title="CareerPath AI - Professional Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database & AI Services ---
@st.cache_resource
def get_db():
    return DatabaseManager()

@st.cache_resource
def get_ai_service():
    return CareerAnalyzerService()

db = get_db()
ai_service = get_ai_service()

# --- Persistent API Key Initialization ---
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = get_persisted_gemini_key()

# --- Theme Controls Initialization (Persistent Across Refreshes) ---
if "app_theme" not in st.session_state:
    url_theme = st.query_params.get("theme", "")
    if str(url_theme).lower() == "dark":
        st.session_state["app_theme"] = "🌙 Modern Dark Glass"
    elif str(url_theme).lower() == "light":
        st.session_state["app_theme"] = "☀️ Executive Light"
    else:
        st.session_state["app_theme"] = "☀️ Executive Light"

is_dark = "Dark" in st.session_state["app_theme"]

# Keep query params in sync with active theme
st.query_params["theme"] = "dark" if is_dark else "light"

# --- Sidebar Initialization ---
with st.sidebar:
    st.markdown("### 🎓 **CareerPath AI**")
    st.caption("Live Enterprise Recommendation Engine")
    st.markdown("---")

# --- Dynamic CSS Injection (Light vs Dark Theme) ---
if is_dark:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        /* Global Background & Typography - DARK THEME */
        .stApp {
            background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        header[data-testid="stHeader"] { background-color: rgba(11, 15, 25, 0.8) !important; }
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        section[data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        
        .hero-banner {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            padding: 28px 36px;
            margin-bottom: 24px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }
        .hero-banner h2 { color: #ffffff !important; }
        .hero-banner p { color: #94a3b8 !important; }

        .exec-card, .course-item {
            background: rgba(30, 41, 59, 0.65);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .exec-card:hover, .course-item:hover {
            transform: translateY(-2deg);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
        }
        .exec-card h3, .exec-card h4, .course-item h4 { color: #ffffff !important; }
        .exec-card p, .course-item p { color: #cbd5e1 !important; }

        .metric-card-light {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
            border: 1px solid rgba(139, 92, 246, 0.35);
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }
        .metric-card-light::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #6366f1, #a855f7);
        }
        .metric-val-light { font-size: 2.3rem; font-weight: 800; color: #818cf8; letter-spacing: -0.5px; }
        .metric-lbl-light { color: #94a3b8; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
        .metric-sub-light { font-size: 0.78rem; color: #a7f3d0; margin-top: 6px; font-weight: 600; }

        .user-chip {
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }
        .user-chip div { color: #f1f5f9 !important; }

        .badge-primary { background-color: rgba(99, 102, 241, 0.25); color: #c7d2fe; border: 1px solid rgba(99, 102, 241, 0.5); }
        .badge-success { background-color: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.5); }
        .badge-warning { background-color: rgba(245, 158, 11, 0.25); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.5); }
        .badge-tag { display: inline-block; padding: 4px 12px; border-radius: 8px; font-size: 0.78rem; font-weight: 700; margin-right: 6px; }

        .skill-adjust-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 12px;
        }

        .ai-rationale-box {
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(129, 140, 248, 0.35);
            border-radius: 10px;
            padding: 10px 14px;
            margin: 10px 0 6px 0;
        }
        .ai-summary-box {
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-left: 4px solid #818cf8;
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }
        .advisor-banner {
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.25) 0%, rgba(147, 51, 234, 0.25) 100%);
            border: 1px solid rgba(139, 92, 246, 0.4);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 20px;
        }

        /* Dark Theme Buttons & Input Overrides */
        .stButton button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
        }
        .stButton button p {
            color: #ffffff !important;
        }
        .stLinkButton a, div[data-testid="stLinkButton"] a {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            text-decoration: none !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease-in-out !important;
        }
        .stLinkButton a p, .stLinkButton a span, div[data-testid="stLinkButton"] a * {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        .stLinkButton a:hover, div[data-testid="stLinkButton"] a:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
            box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        /* Inputs & Selectboxes - DARK THEME */
        .stTextInput input,
        div[data-baseweb="input"] input,
        div[data-baseweb="input"],
        .stSelectbox div[data-baseweb="select"],
        div[data-baseweb="select"] {
            background-color: rgba(30, 41, 59, 0.85) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
        }
        .stTextInput input::placeholder,
        input::placeholder,
        div[data-baseweb="input"] input::placeholder {
            color: #94a3b8 !important;
            -webkit-text-fill-color: #94a3b8 !important;
            opacity: 1 !important;
        }
        div[data-baseweb="select"] * {
            color: #f8fafc !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #0f172a !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }
        ul[role="listbox"] li,
        ul[role="listbox"] li * {
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }
        ul[role="listbox"] li:hover {
            background-color: rgba(99, 102, 241, 0.3) !important;
        }

        /* Main Content Questions Radio Options in Dark Theme */
        .stApp div[data-testid="stRadioButton"],
        .stApp div[data-testid="stRadioButton"] *,
        .stApp div[data-testid="stRadio"],
        .stApp div[data-testid="stRadio"] *,
        .stApp div[data-testid="stMarkdownContainer"] p {
            color: #f8fafc !important;
        }
        .stApp div[data-testid="stRadioButton"] label,
        .stApp div[data-testid="stRadio"] label {
            background-color: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            padding: 10px 16px !important;
            margin-bottom: 6px !important;
            transition: all 0.2s ease-in-out !important;
        }
        .stApp div[data-testid="stRadioButton"] label:hover,
        .stApp div[data-testid="stRadio"] label:hover {
            background-color: rgba(99, 102, 241, 0.25) !important;
            border-color: #6366f1 !important;
        }
        .stApp div[data-testid="stRadioButton"] label p,
        .stApp div[data-testid="stRadioButton"] label span,
        .stApp div[data-testid="stRadioButton"] label div,
        .stApp div[data-testid="stRadio"] label p,
        .stApp div[data-testid="stRadio"] label span {
            color: #f8fafc !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
        }

        /* Fix text area for Dark theme */
        .stTextArea textarea,
        div[data-baseweb="textarea"] {
            background-color: rgba(30, 41, 59, 0.85) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
        }
        .stTextArea textarea::placeholder {
            color: #94a3b8 !important;
            -webkit-text-fill-color: #94a3b8 !important;
            opacity: 1 !important;
        }

        /* Hide Radio Circle Indicator Strictly in Sidebar Navigation */
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label > div:first-child {
            display: none !important;
        }

        /* Navigation Menu Card Button Styling & Increased Font Size */
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label p {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            line-height: 1.5 !important;
            margin: 0 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label {
            padding: 12px 18px !important;
            margin-bottom: 8px !important;
            border-radius: 12px !important;
            background: rgba(30, 41, 59, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            transition: all 0.2s ease-in-out !important;
            cursor: pointer !important;
            width: 100% !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label:hover {
            background: rgba(99, 102, 241, 0.25) !important;
            border-color: rgba(99, 102, 241, 0.5) !important;
            transform: translateX(4px) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label[data-checked="true"],
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label:has(input:checked) {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.4) 0%, rgba(168, 85, 247, 0.4) 100%) !important;
            border: 1px solid #6366f1 !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* Global Background & Typography - LIGHT THEME */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        header[data-testid="stHeader"] { background-color: #f8fafc !important; }
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #cbd5e1;
        }
        section[data-testid="stSidebar"] * { color: #0f172a !important; }

        .hero-banner {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            border: 1px solid #cbd5e1;
            border-radius: 20px;
            padding: 28px 36px;
            margin-bottom: 24px;
            box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
        }
        .hero-banner h2 { color: #0f172a !important; }
        .hero-banner p { color: #475569 !important; }

        .exec-card, .course-item {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .exec-card:hover, .course-item:hover {
            transform: translateY(-2deg);
            box-shadow: 0 8px 24px rgba(79, 70, 229, 0.1);
        }
        .exec-card h3, .exec-card h4, .course-item h4 { color: #0f172a !important; }
        .exec-card p, .course-item p { color: #334155 !important; }

        .metric-card-light {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
            position: relative;
            overflow: hidden;
        }
        .metric-card-light::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
        }
        .metric-val-light { font-size: 2.3rem; font-weight: 800; color: #3730a3; letter-spacing: -0.5px; }
        .metric-lbl-light { color: #475569; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
        .metric-sub-light { font-size: 0.78rem; color: #047857; margin-top: 6px; font-weight: 600; }

        .user-chip {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        }
        .user-chip div { color: #0f172a !important; }

        .badge-primary { background-color: #e0e7ff; color: #3730a3; border: 1px solid #a5b4fc; }
        .badge-success { background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }
        .badge-warning { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
        .badge-tag { display: inline-block; padding: 4px 12px; border-radius: 8px; font-size: 0.78rem; font-weight: 700; margin-right: 6px; }

        .skill-adjust-card {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        }

        .ai-rationale-box {
            background: #f5f3ff;
            border: 1px solid #ddd6fe;
            border-radius: 10px;
            padding: 10px 14px;
            margin: 10px 0 6px 0;
        }
        .ai-summary-box {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 4px solid #4f46e5;
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
        }
        .advisor-banner {
            background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
            border: 1px solid #c7d2fe;
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 20px;
        }

        .deliverables-box {
            font-size: 0.88rem;
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            background: #f8fafc;
            color: #0f172a;
        }

        /* Light Theme Buttons & Input Overrides */
        .stButton button {
            background-color: #4f46e5 !important;
            background: #4f46e5 !important;
            color: #ffffff !important;
            border: 1px solid #4338ca !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.2) !important;
        }
        .stButton button:hover {
            background-color: #4338ca !important;
            background: #4338ca !important;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
        }
        .stButton button p, .stButton button span {
            color: #ffffff !important;
        }
        .stLinkButton a, div[data-testid="stLinkButton"] a {
            background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            text-decoration: none !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .stLinkButton a:hover, div[data-testid="stLinkButton"] a:hover {
            background: linear-gradient(135deg, #047857 0%, #065f46 100%) !important;
            box-shadow: 0 4px 14px rgba(5, 150, 105, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Inputs & Selectboxes - LIGHT THEME */
        .stTextInput input,
        div[data-baseweb="input"] input,
        div[data-baseweb="input"],
        .stSelectbox div[data-baseweb="select"],
        div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
        }
        .stTextInput input {
            border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important;
            background-color: #ffffff !important;
        }
        .stTextInput input::placeholder,
        input::placeholder,
        div[data-baseweb="input"] input::placeholder,
        .stTextArea textarea::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder {
            color: #94a3b8 !important;
            -webkit-text-fill-color: #94a3b8 !important;
            opacity: 1 !important;
        }
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
        }
        ul[role="listbox"] li,
        ul[role="listbox"] li * {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        ul[role="listbox"] li:hover,
        ul[role="listbox"] li[aria-selected="true"] {
            background-color: #e0e7ff !important;
        }

        /* Hide Radio Circle Indicator Strictly in Sidebar Navigation */
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label > div:first-child {
            display: none !important;
        }

        /* Navigation Menu Card Button Styling & Increased Font Size */
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label p {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            line-height: 1.5 !important;
            margin: 0 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label {
            padding: 12px 18px !important;
            margin-bottom: 8px !important;
            border-radius: 12px !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            transition: all 0.2s ease-in-out !important;
            cursor: pointer !important;
            width: 100% !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label:hover {
            background: #e0e7ff !important;
            border-color: #a5b4fc !important;
            transform: translateX(4px) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label[data-checked="true"],
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label:has(input:checked) {
            background: linear-gradient(135deg, #e0e7ff 0%, #ede9fe 100%) !important;
            border: 2px solid #4f46e5 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stRadioButton"] label:has(input:checked) p {
            color: #312e81 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Content Continuation ---
with st.sidebar:
    # 1. NAVIGATION AT THE VERY TOP
    st.markdown("#### 🧭 **Navigation**")
    nav_selection = st.radio(
        "Select Section",
        [
            "📊 Executive Dashboard",
            "🤖 AI Career Analyzer",
            "📚 Curated Learning Path",
            "🎯 Capstone Projects",
            "📝 Skill Verification",
            "📜 Progress History"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Fetch User & Careers
    careers = db.get_careers()
    if not careers:
        careers = [{"career_id": 1, "career_title": "Data Analyst"}, {"career_id": 2, "career_title": "Data Scientist"}]
    career_map = {c["career_title"]: c["career_id"] for c in careers}

    user_id = 1
    user = db.get_user(user_id)

    # 2. ACTIVE USER PROFILE
    st.markdown("#### 👤 **Active User Profile**")
    user_name = user.get('name', 'Yash') if (user and isinstance(user, dict)) else 'Yash'
    user_goal = user.get('career_title', 'Data Analyst') if (user and isinstance(user, dict)) else 'Data Analyst'
    user_hours = user.get('study_hours_per_week', 12) if (user and isinstance(user, dict)) else 12

    st.markdown(f"""
    <div class="user-chip">
        <div style="font-weight: 800; font-size: 1.25rem; margin-bottom: 4px;">{user_name}</div>
        <div style="font-size: 0.88rem; opacity: 0.9; font-weight: 600; margin-bottom: 12px;">🟢 Active Learner</div>
        <div style="font-size: 1.02rem; border-top: 1px solid rgba(128,128,128,0.2); padding-top: 10px; line-height: 1.7;">
            <div>🎯 Target: <strong>{user_goal}</strong></div>
            <div>⏱️ Time Spent: <strong>2 hrs/day</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. CAREER GOAL SELECTOR
    st.markdown("#### 🎯 **Career Goal Selector**")
    career_options = list(career_map.keys())
    default_idx = 0
    if user and isinstance(user, dict) and user.get("career_title") in career_options:
        default_idx = career_options.index(user["career_title"])

    selected_career = st.selectbox(
        "Select Target Role",
        options=career_options,
        index=default_idx,
        label_visibility="collapsed"
    )

    career_id = career_map.get(selected_career, 1)

    # 4. GOOGLE GEMINI AI KEY (PERSISTENT STORAGE)
    st.markdown("---")
    st.markdown("#### 🔑 **Google Gemini AI Key**")
    current_key_val = st.session_state.get("gemini_api_key", "").strip()
    sidebar_key = st.text_input(
        "Gemini API Key (Free)",
        type="password",
        placeholder="AIzaSy...",
        value=current_key_val,
        help="Saved securely until you click 'Delete Key'."
    )
    if sidebar_key != current_key_val:
        st.session_state["gemini_api_key"] = sidebar_key
        st.session_state["custom_api_key"] = sidebar_key
        save_persisted_gemini_key(sidebar_key)

    col_s1, col_s2 = st.columns([1.1, 1])
    with col_s1:
        st.markdown("<div style='margin-top: 6px;'><a href='https://aistudio.google.com/app/apikey' target='_blank' style='font-size: 0.78rem; font-weight: 700; color: #4f46e5; text-decoration: underline;'>Get Free Key ↗</a></div>", unsafe_allow_html=True)
    with col_s2:
        if current_key_val:
            if st.button("🗑️ Delete Key", key="btn_del_key_sidebar", help="Permanently erase API key from memory and storage", use_container_width=True):
                delete_persisted_gemini_key()
                st.session_state["gemini_api_key"] = ""
                st.session_state["custom_api_key"] = ""
                st.toast("🗑️ API Key completely deleted.")
                st.rerun()

    st.markdown("""
    <div style="font-size: 0.74rem; color: #64748b; line-height: 1.35; margin-top: 6px; padding: 6px 8px; background: rgba(148, 163, 184, 0.08); border-radius: 6px; border: 1px dashed rgba(148, 163, 184, 0.3);">
        💾 <strong>Saved:</strong> Key is stored for your active application use until you click <u>Delete Key</u>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 0.8rem;'>🟢 Live Prototype v1.0</div>", unsafe_allow_html=True)

# --- Main Header & Right-Aligned Theme Controls ---
col_banner, col_theme = st.columns([3.2, 1.0], vertical_alignment="center")

with col_banner:
    st.markdown(f"""
    <div class="hero-banner" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0;">
        <div>
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">Smart Career Path Recommender</h2>
            <p style="margin: 4px 0 0 0; font-size: 0.95rem;">
                Real-time skill gap analysis and personalized roadmap for <strong>{selected_career}</strong>
            </p>
        </div>
        <div>
            <span class="badge-tag badge-primary" style="font-size: 0.9rem; padding: 6px 14px;">Target: {selected_career}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_theme:
    st.markdown("<div style='font-size: 0.82rem; font-weight: 700; margin-bottom: 4px; text-align: center;'>🎨 App Theme</div>", unsafe_allow_html=True)
    is_dark_active = "Dark" in st.session_state.get("app_theme", "☀️ Executive Light")
    theme_btn_text = "☀️   Switch to Light   🌙" if is_dark_active else "☀️   Switch to Dark   🌙"
    if st.button(theme_btn_text, key="single_theme_toggle_btn", use_container_width=True):
        if is_dark_active:
            st.session_state["app_theme"] = "☀️ Executive Light"
            st.query_params["theme"] = "light"
        else:
            st.session_state["app_theme"] = "🌙 Modern Dark Glass"
            st.query_params["theme"] = "dark"
        st.rerun()

# --- TAB 1: EXECUTIVE DASHBOARD ---
if nav_selection == "📊 Executive Dashboard":
    user_skills = db.get_user_skills(user_id) if user_id else {}
    career_reqs = db.get_career_skills(career_id) if career_id else []

    df_data = []
    total_req_level = 0
    total_curr_level = 0

    for req in career_reqs:
        s_id = req.get("skill_id")
        s_name = req.get("skill_name", "Skill")
        target = req.get("required_level", 3)
        current = user_skills.get(s_id, 0)
        gap = max(0, target - current)

        total_req_level += target
        total_curr_level += min(target, current)

        df_data.append({
            "Skill": s_name,
            "Current Level": current,
            "Target Required": target,
            "Gap": gap,
            "Importance": req.get("importance", 0.8),
            "Category": req.get("category", "General")
        })

    # Sample Data Fallback if no requirements populated
    if not df_data:
        df_data = [
            {"Skill": "Python", "Current Level": 2, "Target Required": 4, "Gap": 2, "Importance": 0.9, "Category": "Programming"},
            {"Skill": "SQL", "Current Level": 3, "Target Required": 4, "Gap": 1, "Importance": 0.9, "Category": "Databases"},
            {"Skill": "Data Visualization", "Current Level": 1, "Target Required": 3, "Gap": 2, "Importance": 0.8, "Category": "Data Science"},
            {"Skill": "Statistics", "Current Level": 1, "Target Required": 3, "Gap": 2, "Importance": 0.7, "Category": "Mathematics"},
            {"Skill": "Excel", "Current Level": 4, "Target Required": 4, "Gap": 0, "Importance": 0.6, "Category": "Data Analysis"},
        ]
        total_curr_level = 11
        total_req_level = 18

    df_skills = pd.DataFrame(df_data)
    readiness = (total_curr_level / total_req_level * 100) if total_req_level > 0 else 0.0
    skills_count = len(df_skills)
    gaps_count = len(df_skills[df_skills["Gap"] > 0]) if "Gap" in df_skills.columns else 0
    study_hours = user.get('study_hours_per_week', 12) if (user and isinstance(user, dict)) else 12

    # Calculate total gap units to estimate learning weeks needed
    total_gap_units = df_skills["Gap"].sum() if "Gap" in df_skills.columns else 0
    est_weeks = max(1.0, (total_gap_units * 8.0) / max(study_hours, 4))

    # --- Executive Greeting Header ---
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 1.75rem; font-weight: 800;">Welcome back, Yash! 👋</h2>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.95rem;">
                    Executive skill diagnostic & readiness tracking for target role: <strong style="color: #6366f1;">{selected_career}</strong>
                </p>
            </div>
            <div>
                <span class="badge-tag badge-success">🟢 Profile Synchronized</span>
                <span class="badge-tag badge-primary">Level: Intermediate</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Metric Row (4 Premium KPI Cards) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{readiness:.1f}%</div>
            <div class="metric-lbl-light">Career Readiness</div>
            <div class="metric-sub-light">📈 +5.2% vs last benchmark</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{skills_count}</div>
            <div class="metric-lbl-light">Target Competencies</div>
            <div class="metric-sub-light" style="color: #818cf8;">🎯 Role Requirements</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{gaps_count}</div>
            <div class="metric-lbl-light">Active Skill Gaps</div>
            <div class="metric-sub-light" style="color: #fcd34d;">⚡ Priority Upgrades</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">~{est_weeks:.1f} wks</div>
            <div class="metric-lbl-light">Est. Time to Target</div>
            <div class="metric-sub-light" style="color: #6ee7b7;">⏱️ @ {study_hours:.0f}h/week capacity</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Dashboard Layout: Left Analytics (Tabs) vs Right Skill Adjuster ---
    col_chart, col_skills = st.columns([1.3, 1.0])

    with col_chart:
        st.markdown("### 📊 Executive Analytics & Gap Diagnostic")
        tab_radar, tab_bars, tab_ai = st.tabs(["🕸️ Skill Radar", "📊 Competency Breakdown", "💡 AI Action Plan"])

        chart_line1 = '#818cf8' if is_dark else '#4f46e5'
        chart_fill1 = 'rgba(129, 140, 248, 0.35)' if is_dark else 'rgba(79, 70, 229, 0.25)'
        chart_grid = '#334155' if is_dark else '#cbd5e1'
        chart_text = '#f8fafc' if is_dark else '#0f172a'

        with tab_radar:
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=df_skills["Current Level"],
                theta=df_skills["Skill"],
                fill='toself',
                name='Yash (Current)',
                line_color=chart_line1,
                fillcolor=chart_fill1
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=df_skills["Target Required"],
                theta=df_skills["Skill"],
                fill='toself',
                name=f'Benchmark ({selected_career})',
                line_color='#ef4444',
                fillcolor='rgba(239, 68, 68, 0.15)'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 5], gridcolor=chart_grid),
                    angularaxis=dict(gridcolor=chart_grid)
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_text, family='Plus Jakarta Sans, sans-serif'),
                legend=dict(orientation="h", y=-0.15),
                margin=dict(l=40, r=40, t=20, b=30),
                height=380
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with tab_bars:
            fig_bars = go.Figure()
            fig_bars.add_trace(go.Bar(
                y=df_skills["Skill"],
                x=df_skills["Current Level"],
                name="Current Level",
                orientation='h',
                marker=dict(color='#6366f1')
            ))
            fig_bars.add_trace(go.Bar(
                y=df_skills["Skill"],
                x=df_skills["Target Required"],
                name="Target Benchmark",
                orientation='h',
                marker=dict(color='#ef4444', opacity=0.6)
            ))
            fig_bars.update_layout(
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_text, family='Plus Jakarta Sans, sans-serif'),
                xaxis=dict(range=[0, 5.2], title="Proficiency Level (0-5)", gridcolor=chart_grid),
                yaxis=dict(autorange="reversed"),
                legend=dict(orientation="h", y=-0.2),
                margin=dict(l=20, r=20, t=20, b=30),
                height=380
            )
            st.plotly_chart(fig_bars, use_container_width=True)

        with tab_ai:
            top_gap = df_skills.sort_values(by="Gap", ascending=False).iloc[0] if len(df_skills) > 0 else None
            top_skill_name = top_gap["Skill"] if top_gap is not None else "Python"
            top_gap_val = top_gap["Gap"] if top_gap is not None else 2

            st.markdown(f"""
            <div class="exec-card" style="border-left: 4px solid #6366f1; margin-top: 10px;">
                <h4 style="margin-top: 0; color: #818cf8;">🚀 Personalized AI Roadmap Strategy</h4>
                <p>Hello <strong>Yash</strong>, based on your current skill matrix for <strong>{selected_career}</strong>:</p>
                <ul style="margin-bottom: 12px; padding-left: 20px; line-height: 1.7;">
                    <li><strong>Highest Impact Focus:</strong> Elevate <strong>{top_skill_name}</strong> by {top_gap_val} level(s) to immediately increase overall career readiness by ~18%.</li>
                    <li><strong>Pace Recommendation:</strong> Allocate <strong>{study_hours:.0f} hours/week</strong> focused on practical projects.</li>
                    <li><strong>Next Milestone:</strong> Complete the <em>{selected_career} Capstone Project</em> after closing your primary gap.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with col_skills:
        st.markdown("### 🎯 AI Competency Diagnostic")
        st.caption("Objective skill determination from diagnostic questions — eliminating manual estimation:")

        # Summary of current assessed competencies
        for idx, row in df_skills.iterrows():
            s_name = row['Skill']
            c_lvl = int(row['Current Level'])
            t_lvl = int(row['Target Required'])
            pct = min(100, int((c_lvl / t_lvl) * 100)) if t_lvl > 0 else 100
            is_met = c_lvl >= t_lvl

            st.markdown(f"""
            <div class="skill-adjust-card" style="padding: 10px 14px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 0.92rem;">{s_name}</span>
                    <span class="badge-tag {'badge-success' if is_met else 'badge-warning'}" style="font-size: 0.78rem;">
                        Level {c_lvl}/{t_lvl} ({pct}%)
                    </span>
                </div>
                <div style="height: 6px; background: rgba(148, 163, 184, 0.2); border-radius: 3px; margin-top: 6px; overflow: hidden;">
                    <div style="height: 100%; width: {pct}%; background: {'#10b981' if is_met else '#6366f1'}; border-radius: 3px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Interactive Diagnostic Assessment Section
        active_key = st.session_state.get("gemini_api_key", "").strip()
        skills_for_quiz = [row['Skill'] for _, row in df_skills.iterrows()]

        quiz_state_key = f"dashboard_quiz_{selected_career}"
        if quiz_state_key not in st.session_state:
            st.session_state[quiz_state_key] = ai_service.generate_diagnostic_quiz(
                selected_career, skills_for_quiz, f"Target role: {selected_career}", active_key
            )

        current_quiz = st.session_state.get(quiz_state_key, [])

        with st.expander("📝 **Take AI Skill Diagnostic Assessment**", expanded=True):
            st.markdown(f"<p style='font-size: 0.88rem; margin-bottom: 12px;'>Answer these <strong>{len(current_quiz)}</strong> practical questions to accurately evaluate your skills for <strong>{selected_career}</strong>:</p>", unsafe_allow_html=True)
            
            user_answers = {}
            for q in current_quiz:
                q_id = q.get("id", 1)
                skill_name = q.get("skill", "General")
                q_text = q.get("question", "")
                opts = q.get("options", [])
                
                st.markdown(f"**Q{q_id}. [{skill_name}]** {q_text}")
                ans = st.radio(
                    f"Options for Q{q_id}",
                    options=range(len(opts)),
                    format_func=lambda i, opts=opts: opts[i],
                    key=f"dash_quiz_opt_{selected_career}_{q_id}",
                    label_visibility="collapsed"
                )
                user_answers[q_id] = ans
                st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed rgba(128,128,128,0.2);'>", unsafe_allow_html=True)

            col_sub1, col_sub2 = st.columns([1.5, 1])
            with col_sub1:
                if st.button("⚡ Submit & Evaluate Skills", key="btn_eval_dash_quiz", type="primary", use_container_width=True):
                    eval_results = ai_service.evaluate_diagnostic_quiz(current_quiz, user_answers)
                    st.session_state[f"quiz_eval_{selected_career}"] = eval_results
                    
                    # Update SQLite database user skills with verified levels
                    all_db_skills = db.get_skills()
                    skill_id_map = {s["skill_name"]: s["skill_id"] for s in all_db_skills}
                    for s_name, verified_lvl in eval_results["verified_skills"].items():
                        if s_name in skill_id_map:
                            db.set_user_skill(user_id, skill_id_map[s_name], verified_lvl)
                    
                    st.toast("🎉 Skills evaluated & synchronized to database!")
                    st.rerun()

            with col_sub2:
                if st.button("🔄 New Questions", key="btn_regen_dash_quiz", use_container_width=True):
                    st.session_state[quiz_state_key] = ai_service.generate_diagnostic_quiz(
                        selected_career, skills_for_quiz, f"Target role: {selected_career}", active_key
                    )
                    st.rerun()

# --- TAB 2: AI CAREER ANALYZER ---
elif nav_selection == "🤖 AI Career Analyzer":
    st.subheader("🤖 AI Career Goal & Skill Profile Analyzer")
    st.caption("Describe your career aspiration, past experience, and study capacity in natural language. Our AI converts your narrative into a structured skill profile, identifies critical gaps, and personalizes your learning path.")

    # 1. Preset Prompts for Fast 1-Click Exploration
    st.markdown("##### ⚡ Quick-Start Scenario Presets")
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p4, col_p5, _ = st.columns(3)

    if "ai_user_prompt" not in st.session_state:
        st.session_state["ai_user_prompt"] = SAMPLE_CAREER_PROMPTS["Data Analyst"]

    with col_p1:
        if st.button("📊 Transition to Data Analyst", key="preset_da", use_container_width=True):
            st.session_state["ai_user_prompt"] = SAMPLE_CAREER_PROMPTS["Data Analyst"]
            st.rerun()
    with col_p2:
        if st.button("🔬 Aspiring Data Scientist", key="preset_ds", use_container_width=True):
            st.session_state["ai_user_prompt"] = SAMPLE_CAREER_PROMPTS["Data Scientist"]
            st.rerun()
    with col_p3:
        if st.button("🤖 AI/ML Engineer Track", key="preset_ml", use_container_width=True):
            st.session_state["ai_user_prompt"] = SAMPLE_CAREER_PROMPTS["AI/ML Engineer"]
            st.rerun()
    with col_p4:
        if st.button("🌐 Full-Stack Web Dev", key="preset_web", use_container_width=True):
            st.session_state["ai_user_prompt"] = SAMPLE_CAREER_PROMPTS["Web Developer"]
            st.rerun()
    with col_p5:
        if st.button("🛡️ Cybersecurity Switch", key="preset_cyber", use_container_width=True):
            st.session_state["ai_user_prompt"] = SAMPLE_CAREER_PROMPTS["Cybersecurity Specialist"]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Natural Language Input Area
    user_input_prompt = st.text_area(
        "📝 Describe Your Background & Career Goal",
        value=st.session_state["ai_user_prompt"],
        height=140,
        placeholder="e.g. I am a junior developer with Python basics wanting to become a Data Scientist. I can study 15 hours a week..."
    )

    # Google Gemini API Key status & synchronization
    sidebar_or_env_key = st.session_state.get("gemini_api_key", "").strip()

    if sidebar_or_env_key:
        col_st1, col_st2 = st.columns([4, 1.2], vertical_alignment="center")
        with col_st1:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 10px 16px; background: {'rgba(99, 102, 241, 0.15)' if is_dark else '#eef2ff'}; border: 1px solid {'rgba(99, 102, 241, 0.4)' if is_dark else '#c7d2fe'}; border-radius: 10px;">
                <span style="font-weight: 700; color: {'#a5b4fc' if is_dark else '#3730a3'};">🔑 Google Gemini AI Key:</span> 
                <span style="color: {'#e2e8f0' if is_dark else '#0f172a'}; font-size: 0.9rem; margin: 0 8px;">{'•' * 18}</span>
                <span class="badge-tag badge-success" style="font-size: 0.8rem;">Saved & Ready</span>
            </div>
            """, unsafe_allow_html=True)
        with col_st2:
            if st.button("🗑️ Delete Key", key="btn_del_key_main", use_container_width=True, help="Permanently erase API key from memory and storage"):
                delete_persisted_gemini_key()
                st.session_state["gemini_api_key"] = ""
                st.session_state["custom_api_key"] = ""
                st.toast("🗑️ API Key deleted from storage.")
                st.rerun()

        st.markdown(f"""
        <div style="font-size: 0.8rem; color: {'#94a3b8' if is_dark else '#64748b'}; margin-top: 4px; margin-bottom: 14px;">
            💾 <strong>Persistent Storage:</strong> Your key remains saved for this app across refreshes until you click <u>Delete Key</u>.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("##### 🔑 Google Gemini AI Configuration")
        col_k1, col_k2 = st.columns([3, 1])
        with col_k1:
            custom_key = st.text_input(
                "Enter Google Gemini API Key (100% Free)",
                type="password",
                placeholder="AIzaSy...",
                value="",
                help="Saved securely until you click 'Delete Key'."
            )
            if custom_key:
                st.session_state["gemini_api_key"] = custom_key
                st.session_state["custom_api_key"] = custom_key
                save_persisted_gemini_key(custom_key)
        with col_k2:
            st.markdown("<div style='margin-top: 28px;'><a href='https://aistudio.google.com/app/apikey' target='_blank' style='text-decoration: none;'><button style='width: 100%; height: 38px; border-radius: 8px; border: 1px solid #6366f1; background: #6366f1; color: white; font-weight: 600; cursor: pointer;'>Get Free Key ↗</button></a></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size: 0.8rem; color: {'#94a3b8' if is_dark else '#64748b'}; margin-top: 4px; margin-bottom: 14px;">
            💾 <strong>Persistent:</strong> Keys are stored securely for your application use until you click <u>Delete Key</u>.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Trigger Analysis Button
    if st.button("🚀 Analyze Career Path with Google Gemini", type="primary", use_container_width=True):
        active_key = st.session_state.get("gemini_api_key", os.getenv("GEMINI_API_KEY", "")).strip()
        if not active_key:
            st.warning("⚠️ **Google Gemini API Key is required.** Please enter your free Gemini API key in the Sidebar (or above) or generate one for free at [Google AI Studio](https://aistudio.google.com/app/apikey).")
        else:
            with st.spinner("🧠 Querying Google Gemini AI to extract career goals, match skills taxonomy, and build profile..."):
                try:
                    profile_data = ai_service.analyze_career_prompt(user_input_prompt, active_key)
                    st.session_state["analyzed_profile"] = profile_data
                    st.session_state["ai_user_prompt"] = user_input_prompt
                    st.success("✅ Profile analysis complete! Review your Gemini-detected profile below.")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

    # 4. Show and Edit AI-Detected Profile
    if "analyzed_profile" in st.session_state and st.session_state["analyzed_profile"]:
        prof = st.session_state["analyzed_profile"]
        engine_source = prof.get("source", "Google Gemini 1.5 Flash (Live AI)")

        st.markdown("---")
        st.markdown(f"### 📋 Gemini-Generated Learner Profile & Diagnostics &nbsp;<span class='badge-tag badge-primary' style='font-size: 0.85rem;'>Engine: {engine_source}</span>", unsafe_allow_html=True)

        # Executive Summary & Strategy Callout
        st.markdown(f"""
        <div class="ai-summary-box">
            <h4 style="margin: 0 0 6px 0; color: {'#818cf8' if is_dark else '#4f46e5'};">🎯 Executive Summary</h4>
            <p style="margin: 0 0 10px 0; font-size: 0.95rem;">{prof.get('career_summary', '')}</p>
            <h4 style="margin: 8px 0 4px 0; color: {'#a78bfa' if is_dark else '#6366f1'};">💡 Strategic Upskilling Guidance</h4>
            <p style="margin: 0; font-size: 0.95rem;">{prof.get('learning_strategy', '')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### ✏️ **Review & Edit Detected Profile**")
        st.caption("You can fine-tune any detected attributes or skill levels below before synchronizing to your active learning path:")

        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        
        all_career_titles = list(career_map.keys())
        detected_career = prof.get("target_career", "Data Analyst")
        target_idx = all_career_titles.index(detected_career) if detected_career in all_career_titles else 0
        
        with col_cfg1:
            edit_career = st.selectbox("Target Career Goal", all_career_titles, index=target_idx)
        with col_cfg2:
            exp_options = ["Beginner", "Intermediate", "Advanced"]
            det_exp = prof.get("experience_level", "Beginner")
            exp_idx = exp_options.index(det_exp) if det_exp in exp_options else 0
            edit_exp = st.selectbox("Experience Level", exp_options, index=exp_idx)
        with col_cfg3:
            edit_hours = st.number_input("Study Hours / Week", min_value=2.0, max_value=60.0, value=float(prof.get("study_hours_per_week", 12.0)), step=1.0)

        edit_interests = st.text_input("Core Interests & Focus Areas", value=prof.get("interests", "Data Analysis, Python, SQL"))

        st.markdown("##### 🎯 **AI Skill Diagnostic Assessment (Automated Verification)**")
        st.caption("To avoid manual self-estimation, our AI generated these diagnostic questions from your background narrative to verify your true baseline:")

        detected_skills = prof.get("detected_skills", {})
        all_db_skills = db.get_skills()
        skill_id_map = {s["skill_name"]: s["skill_id"] for s in all_db_skills}
        active_key = st.session_state.get("gemini_api_key", "").strip()

        # Generate or retrieve diagnostic quiz tailored to this prompt
        prompt_quiz_key = f"ai_tab_quiz_{edit_career}_{hash(user_input_prompt) % 10000}"
        if prompt_quiz_key not in st.session_state:
            st.session_state[prompt_quiz_key] = ai_service.generate_diagnostic_quiz(
                edit_career, list(detected_skills.keys()), user_input_prompt, active_key
            )

        ai_tab_quiz = st.session_state.get(prompt_quiz_key, [])

        tab_quiz_answers = {}
        for q in ai_tab_quiz:
            q_id = q.get("id", 1)
            skill_name = q.get("skill", "General")
            q_text = q.get("question", "")
            opts = q.get("options", [])
            
            st.markdown(f"**Q{q_id}. [{skill_name}]** {q_text}")
            ans = st.radio(
                f"Options for AI Tab Q{q_id}",
                options=range(len(opts)),
                format_func=lambda i, opts=opts: opts[i],
                key=f"ai_tab_quiz_opt_{q_id}",
                label_visibility="collapsed"
            )
            tab_quiz_answers[q_id] = ans
            st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed rgba(128,128,128,0.2);'>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. Evaluate and Commit to SQLite Database
        if st.button("💾 Evaluate Diagnostic & Synchronize Profile", type="primary", use_container_width=True):
            eval_res = ai_service.evaluate_diagnostic_quiz(ai_tab_quiz, tab_quiz_answers, detected_skills)
            verified_levels = eval_res["verified_skills"]

            new_career_id = career_map.get(edit_career, 1)
            
            # Update users record in DB
            db.update_user(user_id, user_name, new_career_id, edit_interests, edit_hours)
            
            # Update user skills in DB with verified diagnostic scores
            for s_name, lvl in verified_levels.items():
                if s_name in skill_id_map:
                    db.set_user_skill(user_id, skill_id_map[s_name], lvl)

            st.balloons()
            st.success(f"🎉 Diagnostic Completed! Scored {eval_res['correct_count']}/{eval_res['total_questions']} ({eval_res['score_pct']:.0f}%). Profile synchronized for **{user_name}** targeting **{edit_career}**.")
            st.info("💡 Your Executive Dashboard radar charts and Curated Learning Path courses have been dynamically generated from your diagnostic performance.")
            
            col_nav1, col_nav2 = st.columns(2)
            with col_nav1:
                st.write("👉 View your readiness radar on the **Executive Dashboard**")
            with col_nav2:
                st.write("👉 View your personalized materials in **Curated Learning Path**")

# --- TAB 3: CURATED LEARNING PATH ---
elif nav_selection == "📚 Curated Learning Path":
    st.subheader("📚 Personalized Learning Courses & AI Advisory")
    
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search courses or topics...", placeholder="e.g. SQL, Python, Pandas")
    with col_filter:
        difficulty_filter = st.selectbox("Difficulty Level", ["All Levels", "Beginner", "Intermediate", "Advanced"])

    courses = db.get_all_courses()
    user_skills = db.get_user_skills(user_id) if user_id else {}
    career_reqs = db.get_career_skills(career_id) if career_id else []

    # Build df_skills for high-level strategy overview
    df_data = []
    for req in career_reqs:
        s_id = req.get("skill_id")
        s_name = req.get("skill_name", "Skill")
        target = req.get("required_level", 3)
        current = user_skills.get(s_id, 0)
        gap = max(0, target - current)
        df_data.append({
            "Skill": s_name,
            "Current Level": current,
            "Target Required": target,
            "Gap": gap,
            "Importance": req.get("importance", 0.8)
        })
    df_skills_lp = pd.DataFrame(df_data)
    study_hours_val = user.get('study_hours_per_week', 12) if (user and isinstance(user, dict)) else 12.0

    # 1. AI Curriculum Strategy Banner
    strategy_text = ai_service.generate_curriculum_strategy(selected_career, df_skills_lp, study_hours_val)
    st.markdown(f"""
    <div class="advisor-banner">
        <div style="font-size: 1.05rem; font-weight: 700; color: {'#f8fafc' if is_dark else '#1e1b4b'};">
            🧠 AI Curriculum Advisor
        </div>
        <div style="font-size: 0.95rem; margin-top: 4px; color: {'#e2e8f0' if is_dark else '#334155'};">
            {strategy_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    needed_skill_ids = [r["skill_id"] for r in career_reqs if "skill_id" in r]
    relevant_courses = [c for c in courses if c.get("skill_id") in needed_skill_ids] if needed_skill_ids else courses

    def get_diff_label(d):
        if isinstance(d, int):
            d_map = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Advanced", 5: "Advanced"}
            return d_map.get(d, "Intermediate")
        return str(d) if d else "Intermediate"

    if search_query:
        sq = search_query.lower()
        relevant_courses = [c for c in relevant_courses if sq in c.get('title', '').lower() or sq in c.get('description', '').lower()]
    
    if difficulty_filter != "All Levels":
        relevant_courses = [c for c in relevant_courses if get_diff_label(c.get('difficulty')).lower() == difficulty_filter.lower()]

    st.write(f"Displaying **{len(relevant_courses)}** recommendations aligned with **{selected_career}**")

    for course in relevant_courses:
        platform_name = course.get('provider') or course.get('platform') or course.get('resource_type') or 'Online Provider'
        diff_str = get_diff_label(course.get('difficulty'))
        course_url = course.get('url') or 'https://www.youtube.com'

        # Generate personalized AI explanation for this course
        ai_explanation = ai_service.generate_course_explanation(course, user_skills, career_reqs, user)

        card_html = f"""<div class="course-item">
<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
<div>
<h4 style="margin: 0 0 6px 0;">
<a href="{course_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: inherit;">
{course.get('title', 'Course Title')} <span style="font-size: 0.85em; opacity: 0.7;">↗</span>
</a>
</h4>
<p style="margin: 0 0 10px 0; font-size: 0.9rem;">{course.get('description', '')}</p>
</div>
<a href="{course_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
<span class="badge-tag badge-primary" style="cursor: pointer; white-space: nowrap;">▶️ {platform_name} ↗</span>
</a>
</div>
<div class="ai-rationale-box">
<div style="font-weight: 700; font-size: 0.85rem; color: {'#818cf8' if is_dark else '#4f46e5'}; margin-bottom: 2px;">
💡 Why this is recommended for you:
</div>
<div style="font-size: 0.88rem; line-height: 1.4; color: {'#f1f5f9' if is_dark else '#1e293b'};">
{ai_explanation}
</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
<div>
<span class="badge-tag badge-primary">Skill: {course.get('skill_name', 'General')}</span>
<span class="badge-tag badge-warning">Difficulty: {diff_str}</span>
<span style="font-size: 0.85rem; margin-left: 8px;">⏱️ {course.get('duration_hours', 1.0)} hours | ⭐ {course.get('rating', 4.5)}</span>
</div>
<div>
<a href="{course_url}" target="_blank" rel="noopener noreferrer" style="font-size: 0.85rem; font-weight: 700; color: {'#818cf8' if is_dark else '#4f46e5'}; text-decoration: underline;">
▶️ Watch on YouTube ↗
</a>
</div>
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)

        col_link, col_comp, _ = st.columns([1.6, 1.4, 3])
        with col_link:
            st.link_button("▶️ Watch Course ↗", course_url, use_container_width=True)
        with col_comp:
            c_id = course.get('course_id', 1)
            if st.button("Mark Completed", key=f"btn_comp_{c_id}", use_container_width=True):
                db.record_course_status(user_id, c_id, "Completed")
                st.success(f"Updated milestone for '{course.get('title', 'Course')}'!")
                st.rerun()

# --- TAB 3: CAPSTONE PROJECTS ---
elif nav_selection == "🎯 Capstone Projects":
    st.subheader(f"🛠️ Capstone Projects - {selected_career}")
    st.caption(f"Role-aligned portfolio projects designed to demonstrate benchmark readiness for **{selected_career}**")

    all_projects = db.get_all_projects()
    career_reqs = db.get_career_skills(career_id) if career_id else []
    needed_skill_ids = [r["skill_id"] for r in career_reqs if "skill_id" in r]

    role_projects = [p for p in all_projects if p.get("skill_id") in needed_skill_ids]

    # Sample role-specific projects fallback if database has no mapping for this role
    if not role_projects:
        sample_projects_by_role = {
            "Data Analyst": [
                {
                    "title": "Retail Sales & Profitability Dashboard",
                    "description": "Build an end-to-end interactive dashboard analyzing retail sales trends, profit margins, and regional KPIs using SQL, Excel, and Power BI.",
                    "skill_name": "Data Visualization & SQL",
                    "difficulty": "Intermediate",
                    "deliverables": "Interactive Power BI / Tableau dashboard file, SQL query scripts, and executive summary slide deck."
                },
                {
                    "title": "Customer Retention & Cohort Churn Analysis",
                    "description": "Perform cohort retention analysis and calculate customer lifetime value (CLV) using SQL window functions and Pandas.",
                    "skill_name": "SQL & Data Analysis",
                    "difficulty": "Intermediate",
                    "deliverables": "Jupyter Notebook with EDA, SQL cohort queries, and customer segmentation matrix."
                },
                {
                    "title": "Automated HR Analytics & Attrition Report",
                    "description": "Clean messy employee survey data, construct KPI cards, and identify key drivers of department attrition.",
                    "skill_name": "Excel & Statistics",
                    "difficulty": "Beginner",
                    "deliverables": "Excel automated report with dynamic slicers, pivot charts, and action plan."
                }
            ],
            "Data Scientist": [
                {
                    "title": "E-Commerce Customer Churn Prediction Engine",
                    "description": "Train and evaluate Scikit-Learn classification models (Random Forest, XGBoost) to predict subscriber churn with 88%+ accuracy.",
                    "skill_name": "Machine Learning & Python",
                    "difficulty": "Advanced",
                    "deliverables": "Trained ML model pipeline, feature importance plots, and Streamlit prediction web app."
                },
                {
                    "title": "A/B Test Funnel & Conversion Rate Optimization",
                    "description": "Design two-sample t-tests and chi-square hypothesis tests to analyze website user funnel conversion rates.",
                    "skill_name": "Statistics & Hypothesis Testing",
                    "difficulty": "Intermediate",
                    "deliverables": "Statistical report detailing p-values, confidence intervals, and business deployment recommendations."
                }
            ],
            "AI/ML Engineer": [
                {
                    "title": "Real-Time Defect Detection Computer Vision System",
                    "description": "Train a PyTorch Convolutional Neural Network (CNN) to detect manufacturing defects and deploy as a FastAPI service.",
                    "skill_name": "Deep Learning & Computer Vision",
                    "difficulty": "Advanced",
                    "deliverables": "PyTorch CNN model weights, Dockerized REST API, and latency benchmark report."
                },
                {
                    "title": "RAG-Based Enterprise Document Assistant",
                    "description": "Build a Retrieval-Augmented Generation (RAG) Q&A pipeline using LangChain, Vector DB (Chroma), and LLM API.",
                    "skill_name": "LLMs & Vector Search",
                    "difficulty": "Advanced",
                    "deliverables": "Python vector indexing pipeline, Streamlit chat interface, and evaluation notebook."
                }
            ],
            "Web Developer": [
                {
                    "title": "Full-Stack Modern E-Commerce Platform",
                    "description": "Develop a responsive React/Next.js single page application featuring product search, cart state management, and backend REST APIs.",
                    "skill_name": "React & Web Development",
                    "difficulty": "Intermediate",
                    "deliverables": "Deployed web app on Vercel, clean GitHub repository, and REST API documentation."
                },
                {
                    "title": "Real-Time Collaborative Drag-and-Drop Task Board",
                    "description": "Create an interactive Kanban application with local storage persistence, DOM drag-and-drop, and filtering.",
                    "skill_name": "JavaScript & DOM Manipulation",
                    "difficulty": "Intermediate",
                    "deliverables": "Responsive frontend code, unit tests, and GitHub pages deployment."
                }
            ],
            "Cybersecurity Analyst": [
                {
                    "title": "Network Packet Traffic Inspection & Intrusion Detection",
                    "description": "Write a Python monitoring script using Scapy to analyze network packets, detect port scans, and log suspicious traffic anomalies.",
                    "skill_name": "Cybersecurity & Python Scapy",
                    "difficulty": "Advanced",
                    "deliverables": "Packet analyzer Python tool, sample PCAP audit log, and incident triage report."
                },
                {
                    "title": "Web Application Penetration Test & Security Audit",
                    "description": "Conduct OWASP Top 10 security audit against a sandboxed target web app and compile remediation guidelines.",
                    "skill_name": "Vulnerability Assessment",
                    "difficulty": "Intermediate",
                    "deliverables": "Professional vulnerability assessment report, proof-of-concept exploits, and patch recommendations."
                }
            ]
        }

        role_projects = sample_projects_by_role.get(
            selected_career,
            sample_projects_by_role["Data Analyst"]
        )

    st.write(f"Displaying **{len(role_projects)}** capstone project(s) aligned with **{selected_career}**")

    def get_proj_diff_label(d):
        if isinstance(d, int):
            d_map = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Advanced", 5: "Advanced"}
            return d_map.get(d, "Intermediate")
        return str(d) if d else "Intermediate"

    for proj in role_projects:
        deliverables = proj.get('deliverables') or proj.get('tags') or 'Production codebase, clean documentation, and interactive demo.'
        diff_str = get_proj_diff_label(proj.get('difficulty'))

        st.markdown(f"""
        <div class="exec-card">
            <h3 style="margin-top: 0;">🚀 {proj.get('title', 'Capstone Project')}</h3>
            <p style="font-size: 0.95rem;">{proj.get('description', '')}</p>
            <div style="margin-bottom: 10px;">
                <span class="badge-tag badge-primary">Skill: {proj.get('skill_name', 'General')}</span>
                <span class="badge-tag badge-warning">Difficulty: {diff_str}</span>
            </div>
            <div class="deliverables-box">
                <strong>Key Deliverables:</strong> {deliverables}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: SKILL VERIFICATION ---
elif nav_selection == "📝 Skill Verification":
    st.subheader("📝 Skill Knowledge Check")
    skills = db.get_skills()
    skill_names = [s.get("skill_name", "Skill") for s in skills if "skill_name" in s]
    if not skill_names:
        skill_names = ["Python", "SQL", "Excel", "Data Visualization"]

    selected_skill = st.selectbox("Select Skill Domain to Verify", skill_names)

    skill_id_matches = [s["skill_id"] for s in skills if s.get("skill_name") == selected_skill]
    skill_id = skill_id_matches[0] if skill_id_matches else 1
    questions = db.get_assessments_for_skill(skill_id)

    if questions:
        st.write(f"Answer the **{len(questions)}** questions below to evaluate your proficiency in **{selected_skill}**:")
        score = 0
        for i, q in enumerate(questions, 1):
            q_text = q.get('question', '')
            st.markdown(f"""
            <div class="exec-card" style="padding: 16px 20px; margin-bottom: 8px;">
                <div style="font-weight: 800; font-size: 1.1rem; color: {'#0f172a' if not is_dark else '#f8fafc'}; margin-bottom: 4px;">
                    Question {i} of {len(questions)}
                </div>
                <div style="font-size: 1.02rem; color: {'#334155' if not is_dark else '#cbd5e1'}; font-weight: 600;">
                    {q_text}
                </div>
            </div>
            """, unsafe_allow_html=True)
            options = [q.get("option_a", "A"), q.get("option_b", "B"), q.get("option_c", "C"), q.get("option_d", "D")]
            ans = st.radio(f"Choose option for Question {i}", options, key=f"q_{q.get('assessment_id', i)}", label_visibility="collapsed")
            
            # Map selected text back to option letter ('A', 'B', 'C', 'D') to compare with correct_answer
            opt_map = {
                "A": q.get("option_a"),
                "B": q.get("option_b"),
                "C": q.get("option_c"),
                "D": q.get("option_d")
            }
            selected_letter = None
            for letter, text in opt_map.items():
                if text == ans:
                    selected_letter = letter
                    break

            if selected_letter and selected_letter.strip().upper() == str(q.get("correct_answer")).strip().upper():
                score += 1

        if st.button("Submit Assessment Verification", type="primary"):
            final_pct = (score / len(questions)) * 100
            st.balloons()
            st.success(f"Assessment Complete! Verification Score: **{score}/{len(questions)}** ({final_pct:.0f}%)")
    else:
        st.info(f"No verification assessment modules currently loaded for {selected_skill}.")

# --- TAB 5: PROGRESS HISTORY ---
elif nav_selection == "📜 Progress History":
    st.subheader("📜 Certified Learning History")
    history = db.get_user_learning_history(user_id)

    if history:
        col_hist_info, col_clear = st.columns([3, 1])
        with col_hist_info:
            st.write(f"Displaying **{len(history)}** completed course milestone(s) for **Yash**:")
        with col_clear:
            if st.button("🗑️ Clear All History", key="btn_clear_all_history"):
                if hasattr(db, "clear_user_learning_history"):
                    db.clear_user_learning_history(user_id)
                else:
                    with db.get_connection() as conn:
                        conn.execute("DELETE FROM learning_history WHERE user_id = ?", (user_id,))
                        conn.commit()
                st.success("Progress history cleared successfully!")
                st.rerun()

        for idx, item in enumerate(history):
            h_id = item.get("history_id", idx)
            c_title = item.get("title", "Course Title")
            s_domain = item.get("skill_name", "General")
            date_comp = item.get("completion_date", "Recently")
            c_url = item.get("url") or "https://www.youtube.com"

            col_card, col_del = st.columns([4, 1])
            with col_card:
                st.markdown(f"""
                <div class="exec-card" style="margin-bottom: 8px; padding: 16px 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0 0 4px 0; font-size: 1.1rem; color: {'#f8fafc' if is_dark else '#0f172a'};">
                                <a href="{c_url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: inherit;">
                                    {c_title} ↗
                                </a>
                            </h4>
                            <p style="margin: 0; font-size: 0.9rem; color: {'#cbd5e1' if is_dark else '#475569'};">
                                Skill Domain: <strong>{s_domain}</strong> &nbsp;•&nbsp; Completed: <strong>{date_comp}</strong>
                                &nbsp;•&nbsp; <a href="{c_url}" target="_blank" rel="noopener noreferrer" style="color: {'#818cf8' if is_dark else '#4f46e5'}; font-weight: 700;">▶️ Watch Again on YouTube ↗</a>
                            </p>
                        </div>
                        <span class="badge-tag badge-success">Completed</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"btn_del_hist_{h_id}_{idx}"):
                    if hasattr(db, "delete_learning_history_item"):
                        db.delete_learning_history_item(h_id)
                    else:
                        with db.get_connection() as conn:
                            conn.execute("DELETE FROM learning_history WHERE history_id = ?", (h_id,))
                            conn.commit()
                    st.success(f"Deleted milestone: {c_title}")
                    st.rerun()
    else:
        st.info("No completed milestones logged yet. Explore 'Curated Learning Path' to log completions!")
