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
from utils.constants import SKILL_LEVELS, SUPPORTED_CAREERS
from utils.helpers import get_skill_level_label, format_percentage

# --- Page Configuration ---
st.set_page_config(
    page_title="CareerPath AI - Professional Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database Connection ---
@st.cache_resource
def get_db():
    return DatabaseManager()

db = get_db()

# --- Theme Controls Initialization ---
if "app_theme" not in st.session_state:
    st.session_state["app_theme"] = "☀️ Executive Light"

is_dark = "Dark" in st.session_state["app_theme"]

# --- Sidebar Initialization ---
with st.sidebar:
    st.markdown("### 🎓 **CareerPath AI**")
    st.caption("Live Enterprise Recommendation Engine")
    st.markdown("---")

# --- Dynamic CSS Injection (Light vs Dark Theme) ---
if is_dark:
    st.markdown("""
    <style>
        /* Global Background & Typography - DARK THEME */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        header[data-testid="stHeader"] { background-color: rgba(15, 23, 42, 0.8) !important; }
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        section[data-testid="stSidebar"] * { color: #f1f5f9 !important; }
        
        .hero-banner {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        .hero-banner h2 { color: #ffffff !important; }
        .hero-banner p { color: #cbd5e1 !important; }

        .exec-card, .course-item {
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
        .exec-card h3, .exec-card h4, .course-item h4 { color: #ffffff !important; }
        .exec-card p, .course-item p { color: #cbd5e1 !important; }

        .metric-card-light {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%);
            border: 1px solid rgba(139, 92, 246, 0.4);
            border-radius: 12px;
            padding: 16px 20px;
            text-align: center;
        }
        .metric-val-light { font-size: 2.1rem; font-weight: 800; color: #a5b4fc; }
        .metric-lbl-light { color: #94a3b8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }

        .user-chip {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }
        .user-chip div { color: #f1f5f9 !important; }

        .badge-primary { background-color: rgba(99, 102, 241, 0.3); color: #c7d2fe; border: 1px solid #6366f1; }
        .badge-success { background-color: rgba(16, 185, 129, 0.3); color: #6ee7b7; border: 1px solid #10b981; }
        .badge-warning { background-color: rgba(245, 158, 11, 0.3); color: #fcd34d; border: 1px solid #f59e0b; }
        .badge-tag { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 6px; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        /* Global Background & Typography - LIGHT THEME */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        header[data-testid="stHeader"] { background-color: #f8fafc !important; }
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0;
        }
        section[data-testid="stSidebar"] * { color: #1e293b !important; }

        .hero-banner {
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 24px 32px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        }
        .hero-banner h2 { color: #0f172a !important; }
        .hero-banner p { color: #64748b !important; }

        .exec-card, .course-item {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        }
        .exec-card h3, .exec-card h4, .course-item h4 { color: #0f172a !important; }
        .exec-card p, .course-item p { color: #334155 !important; }

        .metric-card-light {
            background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
            border: 1px solid #c7d2fe;
            border-radius: 12px;
            padding: 16px 20px;
            text-align: center;
        }
        .metric-val-light { font-size: 2.1rem; font-weight: 800; color: #3730a3; }
        .metric-lbl-light { color: #475569; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }

        .user-chip {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }
        .user-chip div { color: #0f172a !important; }

        .badge-primary { background-color: #e0e7ff; color: #3730a3; }
        .badge-success { background-color: #dcfce7; color: #15803d; }
        .badge-warning { background-color: #fef3c7; color: #b45309; }
        .badge-tag { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-right: 6px; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Content Continuation ---
with st.sidebar:
    # Fetch User & Careers
    careers = db.get_careers()
    if not careers:
        careers = [{"career_id": 1, "career_title": "Data Analyst"}, {"career_id": 2, "career_title": "Data Scientist"}]
    career_map = {c["career_title"]: c["career_id"] for c in careers}

    user_id = 1
    user = db.get_user(user_id)

    st.markdown("#### 👤 **Active User Profile**")
    if user and isinstance(user, dict):
        st.markdown(f"""
        <div class="user-chip">
            <div style="font-weight: 700; font-size: 1rem;">{user.get('name', 'Alex Morgan')}</div>
            <div style="font-size: 0.85rem;">Target Goal: <strong>{user.get('career_title', 'Data Analyst')}</strong></div>
            <div style="font-size: 0.85rem;">Commitment: <strong>{user.get('study_hours_per_week', 12)} hrs/wk</strong></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="user-chip">
            <div style="font-weight: 700; font-size: 1rem;">Alex Morgan (Demo User)</div>
            <div style="font-size: 0.85rem;">Target Goal: <strong>Data Analyst</strong></div>
            <div style="font-size: 0.85rem;">Commitment: <strong>12 hrs/wk</strong></div>
        </div>
        """, unsafe_allow_html=True)

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

    st.markdown("---")
    st.markdown("#### 🧭 **Navigation**")
    nav_selection = st.radio(
        "Select Section",
        ["📊 Executive Dashboard", "📚 Curated Learning Path", "🎯 Capstone Projects", "📝 Skill Verification", "📜 Progress History"],
        label_visibility="collapsed"
    )

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
    st.selectbox(
        "🎨 **App Theme**",
        ["☀️ Executive Light", "🌙 Modern Dark Glass"],
        key="app_theme"
    )

# --- TAB 1: EXECUTIVE DASHBOARD ---
if nav_selection == "📊 Executive Dashboard":
    st.subheader("Career Readiness & Skill Analytics")

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

    # Metric Row (4 Boxes)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{readiness:.1f}%</div>
            <div class="metric-lbl-light">Career Readiness</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{skills_count}</div>
            <div class="metric-lbl-light">Required Skills</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{gaps_count}</div>
            <div class="metric-lbl-light">Skill Gaps Remaining</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card-light">
            <div class="metric-val-light">{study_hours:.0f}h</div>
            <div class="metric-lbl-light">Weekly Capacity</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Layout Columns
    col_chart, col_skills = st.columns([1.2, 1])

    with col_chart:
        st.markdown("#### 🎯 **Skill Alignment Radar Chart**")
        fig = go.Figure()
        
        chart_line1 = '#a5b4fc' if is_dark else '#4f46e5'
        chart_fill1 = 'rgba(165, 180, 252, 0.3)' if is_dark else 'rgba(79, 70, 229, 0.2)'
        chart_grid = '#334155' if is_dark else '#e2e8f0'
        chart_text = '#f8fafc' if is_dark else '#0f172a'

        fig.add_trace(go.Scatterpolar(
            r=df_skills["Current Level"],
            theta=df_skills["Skill"],
            fill='toself',
            name='Current Skill Level',
            line_color=chart_line1,
            fillcolor=chart_fill1
        ))
        fig.add_trace(go.Scatterpolar(
            r=df_skills["Target Required"],
            theta=df_skills["Skill"],
            fill='toself',
            name='Required Benchmark',
            line_color='#ef4444',
            fillcolor='rgba(239, 68, 68, 0.15)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 5], gridcolor=chart_grid),
                angularaxis=dict(gridcolor=chart_grid)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=chart_text, family='sans-serif'),
            legend=dict(orientation="h", y=-0.15),
            margin=dict(l=40, r=40, t=20, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_skills:
        st.markdown("#### ⚡ **Interactive Skill Level Adjuster**")
        st.caption("Adjust your proficiency level to see live readiness updates:")
        
        for idx, row in df_skills.iterrows():
            with st.container():
                st.write(f"**{row['Skill']}** (Target: Level {row['Target Required']})")
                new_level = st.slider(
                    f"Proficiency Level ({row['Skill']})",
                    min_value=0, max_value=5,
                    value=int(row['Current Level']),
                    key=f"skill_slider_{row['Skill']}",
                    label_visibility="collapsed"
                )
                if new_level != row['Current Level']:
                    s_id = [s['skill_id'] for s in db.get_skills() if s['skill_name'] == row['Skill']][0]
                    db.set_user_skill(user_id, s_id, new_level)
                    st.rerun()

# --- TAB 2: CURATED LEARNING PATH ---
elif nav_selection == "📚 Curated Learning Path":
    st.subheader("📚 Personalized Learning Courses")
    
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search courses or topics...", placeholder="e.g. SQL, Python, Pandas")
    with col_filter:
        difficulty_filter = st.selectbox("Difficulty Level", ["All Levels", "Beginner", "Intermediate", "Advanced"])

    courses = db.get_all_courses()
    user_skills = db.get_user_skills(user_id) if user_id else {}
    career_reqs = db.get_career_skills(career_id) if career_id else []

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

        st.markdown(f"""
        <div class="course-item">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h4 style="margin: 0 0 6px 0;">{course.get('title', 'Course Title')}</h4>
                    <p style="margin: 0 0 10px 0; font-size: 0.9rem;">{course.get('description', '')}</p>
                </div>
                <span class="badge-tag badge-primary">{platform_name}</span>
            </div>
            <div>
                <span class="badge-tag badge-primary">Skill: {course.get('skill_name', 'General')}</span>
                <span class="badge-tag badge-warning">Difficulty: {diff_str}</span>
                <span style="font-size: 0.85rem; margin-left: 8px;">⏱️ {course.get('duration_hours', 1.0)} hours | ⭐ {course.get('rating', 4.5)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_act, _ = st.columns([1, 4])
        with col_act:
            c_id = course.get('course_id', 1)
            if st.button(f"Mark Completed", key=f"btn_comp_{c_id}"):
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
            <div style="font-size: 0.88rem; padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
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
            st.markdown(f"""
            <div class="exec-card" style="padding: 16px 20px; margin-bottom: 12px;">
                <strong>Question {i} of {len(questions)}:</strong> {q.get('question', '')}
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
        df_hist = pd.DataFrame(history)
        cols_to_show = [c for c in ["title", "skill_name", "status", "completion_date"] if c in df_hist.columns]
        if cols_to_show:
            st.dataframe(
                df_hist[cols_to_show].rename(columns={
                    "title": "Course Title",
                    "skill_name": "Skill Domain",
                    "status": "Status",
                    "completion_date": "Date Completed"
                }),
                use_container_width=True
            )
        else:
            st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No completed milestones logged yet. Explore 'Curated Learning Path' to log completions!")
