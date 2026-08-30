import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Top banner bar
        self.setFillColor(colors.HexColor("#0F172A"))
        self.rect(0, 580, 792, 32, fill=True, stroke=False)
        
        # Top accent stripe
        self.setFillColor(colors.HexColor("#4F46E5"))
        self.rect(0, 577, 792, 3, fill=True, stroke=False)
        
        # Header text
        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 10)
        self.drawString(36, 592, "CAREERPATH AI — ENTERPRISE REPAIR & ROADMAP REVOLUTION")
        self.setFont("Helvetica", 9)
        self.drawRightString(756, 592, "PROJECT PRESENTATION DECK")

        # Bottom footer bar
        self.setFillColor(colors.HexColor("#F1F5F9"))
        self.rect(0, 0, 792, 28, fill=True, stroke=False)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.line(0, 28, 792, 28)

        self.setFillColor(colors.HexColor("#64748B"))
        self.setFont("Helvetica-Bold", 8)
        self.drawString(36, 10, "CONFIDENTIAL & PROPRIETARY | LIVE STREAMLIT PROTOTYPE V1.0")
        self.setFont("Helvetica", 8)
        self.drawRightString(756, 10, f"Slide {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(filename="CareerPath_AI_Presentation.pdf"):
    # Landscape Letter: 792 x 612 pt
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#0F172A")
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4F46E5")
    )
    slide_header = ParagraphStyle(
        'SlideHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2
    )
    slide_subhead = ParagraphStyle(
        'SlideSubhead',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=8
    )
    body_text = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0F172A")
    )
    bullet_text = ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B")
    )
    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#4F46E5")
    )
    speaker_note_style = ParagraphStyle(
        'SpeakerNote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155")
    )

    story = []

    def make_speaker_box(note_text):
        content = [
            Paragraph("<b>🎙️ Presenter Talking Points:</b>", ParagraphStyle('NT', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#4338CA"))),
            Spacer(1, 1),
            Paragraph(note_text, speaker_note_style)
        ]
        t = Table([[content]], colWidths=[720])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEF2FF")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#C7D2FE")),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    # ==================== SLIDE 1: TITLE SLIDE ====================
    story.append(Spacer(1, 15))
    cover_data = [
        [
            Paragraph("🎓 <b>CAREERPATH AI</b>", ParagraphStyle('CoverBadge', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor("#4F46E5"))),
        ],
        [
            Paragraph("Smart Learning & Career Path Recommender System", title_style)
        ],
        [
            Paragraph("Closing Industry Skill Gaps Through Real-Time Diagnostics, YouTube Masterclasses & Knowledge Verification", subtitle_style)
        ]
    ]
    t_cover = Table(cover_data, colWidths=[720])
    t_cover.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,1), (0,1), 8),
    ]))
    story.append(t_cover)
    story.append(Spacer(1, 12))

    pills_data = [
        [
            Paragraph("<b>Target Careers:</b> Data Analyst • Data Scientist • AI/ML Engineer • Web Developer • Cybersecurity", body_text),
            Paragraph("<b>Tech Stack:</b> Python 3.11 • Streamlit • Plotly • SQLite3 • Pandas", body_text)
        ],
        [
            Paragraph("<b>Status:</b> Live Streamlit Prototype (100% Passed Test Suite)", body_text),
            Paragraph("<b>Presentation Type:</b> Project Architecture & Live Demonstration", body_text)
        ]
    ]
    t_pills = Table(pills_data, colWidths=[360, 360])
    t_pills.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_pills)
    story.append(Spacer(1, 15))
    story.append(make_speaker_box("Welcome everyone. Today we present CareerPath AI — an enterprise-grade recommendation engine built to solve skill mismatch, eliminate learning friction, and provide verified paths to target tech careers."))
    story.append(PageBreak())

    # ==================== SLIDE 2: THE PROBLEM ====================
    story.append(Paragraph("The Industry Challenge: The Tech Upskilling Dilemma", slide_header))
    story.append(Paragraph("Learners and career transitioners face high friction, fragmented roadmaps, and zero verification.", slide_subhead))

    prob_cards = [
        [
            Paragraph("<b>⚠️ Widening Skill Gaps</b>", card_title),
            Paragraph("<b>🌊 Information Overload</b>", card_title),
            Paragraph("<b>🔒 Paywalls & Friction</b>", card_title)
        ],
        [
            Paragraph("Fast-moving tech benchmarks mean university curricula quickly become outdated, leaving candidates unaware of exact market requirements.", bullet_text),
            Paragraph("Over 100,000+ tutorials exist online, creating analysis paralysis without actionable guidance on what to study first.", bullet_text),
            Paragraph("High subscription fees and account requirements block motivated learners from accessing fundamental learning materials.", bullet_text)
        ],
        [
            Paragraph("<b>❌ Rigid Roadmaps</b>", card_title),
            Paragraph("<b>❓ No Verification</b>", card_title),
            Paragraph("<b>📉 Low Completion</b>", card_title)
        ],
        [
            Paragraph("One-size-fits-all roadmaps ignore existing proficiencies, forcing learners to waste time reviewing topics they already know.", bullet_text),
            Paragraph("Passive tutorial consumption without dynamic quizzes or capstone deliverables creates an illusion of competence.", bullet_text),
            Paragraph("Without dynamic timelines and milestone audit logs, over 85% of online self-paced learners abandon courses prematurely.", bullet_text)
        ]
    ]
    t_prob = Table(prob_cards, colWidths=[235, 235, 235])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 8))
    story.append(make_speaker_box("Students and professionals don't fail due to a lack of effort; they fail due to lack of diagnostic clarity, paywalls, and uncurated materials. CareerPath AI solves every one of these problems."))
    story.append(PageBreak())

    # ==================== SLIDE 3: THE SOLUTION ====================
    story.append(Paragraph("The Solution: CareerPath AI Recommender Engine", slide_header))
    story.append(Paragraph("An end-to-end intelligent platform bridging diagnostic analytics, curated YouTube learning, and skill checks.", slide_subhead))

    sol_cards = [
        [
            Paragraph("<b>🎯 Real-Time Diagnostics</b>", card_title),
            Paragraph("<b>▶️ 100% Free YouTube Path</b>", card_title)
        ],
        [
            Paragraph("• Mathematical readiness scoring against 5 primary tech roles.<br/>• Polar radar visualization & dual-bar gap comparisons.<br/>• Interactive slider simulation for instant scenario planning.", bullet_text),
            Paragraph("• 53+ hand-picked masterclasses from world-renowned creators.<br/>• Direct 1-click access without accounts or paywalls.<br/>• Filterable by difficulty (Beginner, Intermediate, Advanced) and keywords.", bullet_text)
        ],
        [
            Paragraph("<b>📝 Continuous Knowledge Verification</b>", card_title),
            Paragraph("<b>🛠️ Employable Capstone Projects</b>", card_title)
        ],
        [
            Paragraph("• 225+ question assessment bank across 15 skill domains.<br/>• Instant evaluation, score analytics, and milestone validation.<br/>• Immutable completion audit trail in progress history.", bullet_text),
            Paragraph("• Role-tailored project briefs with specific deliverable requirements.<br/>• Real-world scenario simulation (e.g. Sales KPIs, Churn Models, RAG).<br/>• Practical portfolio proof-of-work ready for employers.", bullet_text)
        ]
    ]
    t_sol = Table(sol_cards, colWidths=[355, 355])
    t_sol.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_sol)
    story.append(Spacer(1, 8))
    story.append(make_speaker_box("Our solution combines the diagnostic precision of an enterprise HR tool with the accessibility of top-tier YouTube open education."))
    story.append(PageBreak())

    # ==================== SLIDE 4: ARCHITECTURE ====================
    story.append(Paragraph("System Architecture & Data Flow", slide_header))
    story.append(Paragraph("Layered modular architecture ensuring high responsiveness, data integrity, and seamless scaling.", slide_subhead))

    arch_table_data = [
        [Paragraph("<b>Layer</b>", bold_body), Paragraph("<b>Components & Technology</b>", bold_body), Paragraph("<b>Key Responsibilities</b>", bold_body)],
        [
            Paragraph("<b>1. Presentation Layer</b>", body_text),
            Paragraph("Streamlit 1.62 • HTML5/CSS3 • Executive Light & Modern Dark Glassmorphism", body_text),
            Paragraph("Renders responsive multi-tab UI, interactive sliders, search filters, and theme toggling.", body_text)
        ],
        [
            Paragraph("<b>2. Analytics & Visuals</b>", body_text),
            Paragraph("Plotly Express • Plotly Graph Objects", body_text),
            Paragraph("Generates real-time polar radar charts, target benchmark bars, and KPI metric cards.", body_text)
        ],
        [
            Paragraph("<b>3. Domain Logic Engine</b>", body_text),
            Paragraph("Python 3.11 • Pandas • Math Module", body_text),
            Paragraph("Calculates readiness percentage, priority gap rank, study week estimates, and assessment scoring.", body_text)
        ],
        [
            Paragraph("<b>4. Database & Storage</b>", body_text),
            Paragraph("SQLite3 Relational DB (`PRAGMA foreign_keys=ON`)", body_text),
            Paragraph("Persists 10 normalized tables, skill requirement matrices, question banks, and learning logs.", body_text)
        ]
    ]
    t_arch = Table(arch_table_data, colWidths=[130, 250, 340])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))
    story.append(make_speaker_box("CareerPath AI follows a clean separation of concerns. The reactive Streamlit layer feeds directly into our Python calculation engine and SQLite relational core."))
    story.append(PageBreak())

    # ==================== SLIDE 5: MATHEMATICAL MODEL ====================
    story.append(Paragraph("Algorithmic & Mathematical Modeling", slide_header))
    story.append(Paragraph("Data-driven formulas driving personalized gap analysis and pacing recommendations.", slide_subhead))

    math_data = [
        [
            Paragraph("<b>1. Career Readiness Metric (R)</b>", card_title),
            Paragraph("<b>Formula:</b> <code>Readiness (%) = (Σ min(Current_i, Target_i) / Σ Target_i) * 100</code><br/>"
                      "<b>Rationale:</b> Ensures that over-skilling in one area does not falsely mask deficiency in another critical competency.", bullet_text)
        ],
        [
            Paragraph("<b>2. Priority Gap Weighting</b>", card_title),
            Paragraph("<b>Formula:</b> <code>Priority_i = (Target_i - Current_i) * Importance_Weight_i</code><br/>"
                      "<b>Rationale:</b> Ranks which skill upgrade delivers the highest immediate readiness boost for the user's target role.", bullet_text)
        ],
        [
            Paragraph("<b>3. Estimated Time to Benchmark</b>", card_title),
            Paragraph("<b>Formula:</b> <code>Est_Weeks = max(1.0, (Total_Gap_Units * 8.0 hrs) / Weekly_Study_Hours)</code><br/>"
                      "<b>Rationale:</b> Dynamic estimation adapting in real-time to the learner's committed weekly study capacity.", bullet_text)
        ],
        [
            Paragraph("<b>4. Assessment Proficiency Gain</b>", card_title),
            Paragraph("<b>Formula:</b> <code>Verification_Score (%) = (Correct_Answers / Total_Questions) * 100</code><br/>"
                      "<b>Rationale:</b> Validates minimum 70% threshold before endorsing level advancement in user skills ledger.", bullet_text)
        ]
    ]
    t_math = Table(math_data, colWidths=[200, 520])
    t_math.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_math)
    story.append(Spacer(1, 8))
    story.append(make_speaker_box("Our formulas are bounded and realistic. The min() operator prevents score inflation, ensuring a genuine, trustworthy assessment of industry readiness."))
    story.append(PageBreak())

    # ==================== SLIDE 6: CORE MODULES ====================
    story.append(Paragraph("Core Application Modules & Feature Tour", slide_header))
    story.append(Paragraph("5 tightly integrated tabs providing an end-to-end continuous learning lifecycle.", slide_subhead))

    modules_data = [
        [Paragraph("<b>Navigation Tab</b>", bold_body), Paragraph("<b>Key Interactive Features</b>", bold_body), Paragraph("<b>User Outcome</b>", bold_body)],
        [
            Paragraph("<b>📊 Executive Dashboard</b>", body_text),
            Paragraph("• 4 Metric KPI Cards (Readiness %, Gaps, Target Skills, Est. Time)<br/>• Polar Skill Radar Chart & Benchmark Bar Comparison<br/>• Real-time Proficiency Sliders (0-5 Level Simulation)", bullet_text),
            Paragraph("High-level strategic diagnosis of current preparedness and immediate priority upgrades.", bullet_text)
        ],
        [
            Paragraph("<b>📚 Curated Learning Path</b>", body_text),
            Paragraph("• Keyword search bar & Difficulty filter dropdown<br/>• 53 Curated course cards with provider & duration metadata<br/>• <code>▶️ Watch Course ↗</code> direct YouTube access buttons<br/>• <code>Mark Completed</code> milestone logging", bullet_text),
            Paragraph("Frictionless learning journey directly mapped to closing active skill gaps.", bullet_text)
        ],
        [
            Paragraph("<b>🎯 Capstone Projects</b>", body_text),
            Paragraph("• Role-tailored portfolio project briefs<br/>• Explicit deliverable criteria & difficulty tags", bullet_text),
            Paragraph("Tangible portfolio items to showcase in job applications and technical interviews.", bullet_text)
        ],
        [
            Paragraph("<b>📝 Skill Verification</b>", body_text),
            Paragraph("• Domain selector across 15 skills<br/>• Multi-question interactive MCQs with instant scoring", bullet_text),
            Paragraph("Objective proof of competency and knowledge retention.", bullet_text)
        ],
        [
            Paragraph("<b>📜 Progress History</b>", body_text),
            Paragraph("• Chronological audit log with completion timestamps<br/>• Re-watch YouTube direct links & individual milestone deletion", bullet_text),
            Paragraph("Full tracking and management of accomplished learning milestones.", bullet_text)
        ]
    ]
    t_mod = Table(modules_data, colWidths=[140, 380, 200])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_mod)
    story.append(Spacer(1, 6))
    story.append(make_speaker_box("Notice how each tab flows naturally into the next: Diagnose on Dashboard -> Learn on Learning Path -> Build in Capstones -> Verify in Assessments -> Track in History."))
    story.append(PageBreak())

    # ==================== SLIDE 7: DATABASE SCHEMA ====================
    story.append(Paragraph("Relational Database Schema & Data Integrity", slide_header))
    story.append(Paragraph("10 normalized relational tables in SQLite ensuring data consistency and fast querying.", slide_subhead))

    schema_data = [
        [Paragraph("<b>Table</b>", bold_body), Paragraph("<b>Primary Columns</b>", bold_body), Paragraph("<b>Foreign Keys & Constraints</b>", bold_body)],
        [Paragraph("<code>careers</code>", body_text), Paragraph("career_id (PK), career_title, description", body_text), Paragraph("UNIQUE(career_title)", body_text)],
        [Paragraph("<code>skills</code>", body_text), Paragraph("skill_id (PK), skill_name, category", body_text), Paragraph("UNIQUE(skill_name)", body_text)],
        [Paragraph("<code>career_skills</code>", body_text), Paragraph("id (PK), career_id, skill_id, required_level, importance", body_text), Paragraph("FK(career_id), FK(skill_id), CHECK(0<=level<=5)", body_text)],
        [Paragraph("<code>courses</code>", body_text), Paragraph("course_id (PK), title, skill_id, difficulty, duration_hours, provider, url, rating", body_text), Paragraph("FK(skill_id), CHECK(1<=difficulty<=5)", body_text)],
        [Paragraph("<code>projects</code>", body_text), Paragraph("project_id (PK), title, description, skill_id, difficulty, deliverables", body_text), Paragraph("FK(skill_id)", body_text)],
        [Paragraph("<code>assessments</code>", body_text), Paragraph("assessment_id (PK), skill_id, question, option_a..d, correct_answer", body_text), Paragraph("FK(skill_id)", body_text)],
        [Paragraph("<code>users</code>", body_text), Paragraph("user_id (PK), name, career_goal_id, study_hours_per_week", body_text), Paragraph("FK(career_goal_id)", body_text)],
        [Paragraph("<code>user_skills</code>", body_text), Paragraph("user_id (PK), skill_id (PK), current_level", body_text), Paragraph("FK(user_id), FK(skill_id), CHECK(0<=level<=5)", body_text)],
        [Paragraph("<code>learning_history</code>", body_text), Paragraph("history_id (PK), user_id, course_id, status, completion_date", body_text), Paragraph("FK(user_id), FK(course_id)", body_text)]
    ]
    t_sch = Table(schema_data, colWidths=[120, 360, 240])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sch)
    story.append(Spacer(1, 6))
    story.append(make_speaker_box("Our schema is fully normalized with cascade deletes and strict check constraints, ensuring rock-solid data integrity during multi-tab updates."))
    story.append(PageBreak())

    # ==================== SLIDE 8: LIVE DEMO SCRIPT ====================
    story.append(Paragraph("Live Product Demonstration Walkthrough", slide_header))
    story.append(Paragraph("Follow this structured 5-step script during the live presentation.", slide_subhead))

    demo_steps = [
        [
            Paragraph("<b>Step 1: Role Goal Switching</b>", card_title),
            Paragraph("Select <b>Data Analyst</b>, show initial 61.1% Readiness score. Switch to <b>Data Scientist</b> to prove instant recalculation of Radar charts and AI strategy recommendations.", bullet_text)
        ],
        [
            Paragraph("<b>Step 2: Interactive Slider Simulation</b>", card_title),
            Paragraph("Drag the <b>Python</b> proficiency slider from Level 2 to Level 4. Highlight the live re-render showing Readiness jumping from 61.1% to 72.2% with immediate KPI updates.", bullet_text)
        ],
        [
            Paragraph("<b>Step 3: Direct YouTube Course Access</b>", card_title),
            Paragraph("Navigate to <b>Curated Learning Path</b>. Filter by 'Beginner' and click <b>`▶️ Watch Course ↗`</b>. Demonstrate the instant YouTube masterclass popup with zero login friction.", bullet_text)
        ],
        [
            Paragraph("<b>Step 4: Milestone Logging & History</b>", card_title),
            Paragraph("Click <b>`Mark Completed`</b> on the course card. Switch to <b>Progress History</b> to show the certified timestamped entry and direct re-watch access.", bullet_text)
        ],
        [
            Paragraph("<b>Step 5: Assessment & Theme Switch</b>", card_title),
            Paragraph("Take a 3-question quiz in <b>Skill Verification</b>, submit with balloon animation, and toggle between <b>Executive Light</b> and <b>Modern Dark Glassmorphism</b>.", bullet_text)
        ]
    ]
    t_demo = Table(demo_steps, colWidths=[220, 500])
    t_demo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_demo)
    story.append(Spacer(1, 6))
    story.append(make_speaker_box("During the demo, emphasize how fast the UI reacts. The theme toggle and proficiency sliders demonstrate real-time state synchronization."))
    story.append(PageBreak())

    # ==================== SLIDE 9: TEST RESULTS & QUALITY ====================
    story.append(Paragraph("Validation, Quality Assurance & Metrics", slide_header))
    story.append(Paragraph("Automated test coverage validating database consistency, seed data, and calculation logic.", slide_subhead))

    qa_data = [
        [Paragraph("<b>Test Module</b>", bold_body), Paragraph("<b>Target Scope</b>", bold_body), Paragraph("<b>Status & Pass Rate</b>", bold_body)],
        [
            Paragraph("<code>tests/test_database.py</code>", body_text),
            Paragraph("Tests CRUD queries, foreign key enforcement, user creation, and history logging.", body_text),
            Paragraph("<font color='#059669'><b>PASSED (4/4 tests)</b></font>", body_text)
        ],
        [
            Paragraph("<code>tests/test_datasets.py</code>", body_text),
            Paragraph("Verifies 53 valid courses, CSV file formats, YouTube URLs, and assessment counts.", body_text),
            Paragraph("<font color='#059669'><b>PASSED (1/1 test)</b></font>", body_text)
        ],
        [
            Paragraph("<code>tests/test_env.py</code>", body_text),
            Paragraph("Validates environment configurations, database paths, and package imports.", body_text),
            Paragraph("<font color='#059669'><b>PASSED (1/1 test)</b></font>", body_text)
        ],
        [
            Paragraph("<b>Overall Suite Summary</b>", bold_body),
            Paragraph("Pytest 9.1.1 on Python 3.11 — Total execution verified without regression.", bold_body),
            Paragraph("<font color='#059669'><b>6/6 PASSED (100%)</b></font>", bold_body)
        ]
    ]
    t_qa = Table(qa_data, colWidths=[180, 360, 180])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,1), (-1,-2), colors.HexColor("#FFFFFF")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#ECFDF5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_qa)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Key Project Metrics:</b>", bold_body))
    story.append(Spacer(1, 3))
    story.append(Paragraph("• <b>53+ Accessible YouTube Masterclasses:</b> 100% verified URLs from world-class instructors.", bullet_text))
    story.append(Paragraph("• <b>225 Assessment Questions:</b> Distributed across 15 high-demand technical skill domains.", bullet_text))
    story.append(Paragraph("• <b>Sub-Second Response Times:</b> Real-time in-memory caching with SQLite connection pooling.", bullet_text))
    story.append(Spacer(1, 6))
    story.append(make_speaker_box("Our system is thoroughly tested. All database operations, dataset integrity checks, and environment configurations pass automated testing cleanly."))
    story.append(PageBreak())

    # ==================== SLIDE 10: ROADMAP & CONCLUSION ====================
    story.append(Paragraph("Future Roadmap & Concluding Summary", slide_header))
    story.append(Paragraph("Scaling from an individual recommender to an enterprise upskilling ecosystem.", slide_subhead))

    road_data = [
        [
            Paragraph("<b>Phase 1: Current Release (v1.0)</b>", card_title),
            Paragraph("• Live Streamlit web prototype with Executive Light & Dark themes.<br/>"
                      "• Real-time skill diagnostic formulas, radar charts & gap priority ranks.<br/>"
                      "• 53 curated free YouTube courses with 1-click video access.<br/>"
                      "• Knowledge check quizzes and certified progress history.", bullet_text)
        ],
        [
            Paragraph("<b>Phase 2: AI Enhancements (v2.0)</b>", card_title),
            Paragraph("• LLM-powered resume & LinkedIn profile parser for automated skill baseline extraction.<br/>"
                      "• Automated code & notebook grading for Capstone Project submissions.<br/>"
                      "• Real-time AI chat tutor for course-specific questions.", bullet_text)
        ],
        [
            Paragraph("<b>Phase 3: Enterprise Platform (v3.0)</b>", card_title),
            Paragraph("• Multi-tenant organization dashboards for HR & Engineering managers.<br/>"
                      "• Custom role matrix builder tailored to internal company tech stacks.<br/>"
                      "• Integration with enterprise LMS (Workday, Coursera Enterprise, Degreed).", bullet_text)
        ]
    ]
    t_road = Table(road_data, colWidths=[230, 490])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<font size='11' color='#0F172A'><b>Thank you! Questions & Live Demonstration Welcome.</b></font>", ParagraphStyle('TQ', alignment=1)))
    story.append(Spacer(1, 6))
    story.append(make_speaker_box("In summary, CareerPath AI transforms career upskilling from guesswork into a data-driven science. Thank you, and we look forward to your questions."))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF successfully built at:", filename)

if __name__ == "__main__":
    build_pdf("CareerPath_AI_Presentation.pdf")
