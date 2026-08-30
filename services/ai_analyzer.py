"""
AI Career Analyzer Service
Handles natural language career goal parsing, structured profile extraction,
LLM API integration with robust heuristic fallback, and personalized recommendation rationales.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
import requests

from utils.constants import SUPPORTED_CAREERS, SKILL_LEVELS


class CareerAnalyzerService:
    """Provides Google Gemini LLM-driven natural language career profile extraction and rationales."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or ""

    def analyze_career_prompt(self, user_text: str, custom_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse unstructured natural language text into a structured learner profile using Google Gemini 1.5 Flash.
        """
        active_key = (custom_api_key or self.api_key or "").strip()
        user_text_clean = (user_text or "").strip()

        if not user_text_clean:
            return self._get_default_profile()

        if not active_key or len(active_key) < 8:
            raise ValueError(
                "Google Gemini API Key is required. Please provide a free Gemini API key from Google AI Studio (https://aistudio.google.com/app/apikey)."
            )

        gemini_result = self._call_gemini_api(user_text_clean, active_key)
        if gemini_result and self._validate_profile_structure(gemini_result):
            gemini_result["source"] = "Google Gemini 1.5 Flash (Live AI)"
            return gemini_result
        else:
            raise RuntimeError("Google Gemini API returned an invalid response structure.")

    def _call_gemini_api(self, user_text: str, api_key: str) -> Dict[str, Any]:
        """
        Query Google Gemini via REST API with dynamic model discovery (ListModels),
        automatic fallback across available generation models, and strict JSON schema.
        """
        system_instruction = (
            "You are an expert enterprise career counselor and skills diagnostic engine for CareerPath AI.\n"
            "Analyze the user's career description and extract a structured JSON profile.\n\n"
            "TRAINING & DOMAIN INFERENCE RULES:\n"
            "1. 'target_career' MUST be EXACTLY one of:\n"
            "   - 'Data Analyst'\n"
            "   - 'Data Scientist'\n"
            "   - 'AI/ML Engineer'\n"
            "   - 'Web Developer'\n"
            "   - 'Cybersecurity Analyst'\n\n"
            "2. Career Inference from Technologies:\n"
            "   - HTML, CSS, React, JavaScript, Frontend, Fullstack -> 'Web Developer'\n"
            "   - Ethical Hacking, Wireshark, Network Security, Penetration Testing, OWASP -> 'Cybersecurity Analyst'\n"
            "   - Deep Learning, Neural Networks, PyTorch, Transformers, NLP, LLM, Computer Vision -> 'AI/ML Engineer'\n"
            "   - Statistics, Machine Learning, Scikit-Learn, Predictive Modeling -> 'Data Scientist'\n"
            "   - Excel, Power BI, SQL, Data Visualization, Dashboards, Tableau -> 'Data Analyst'\n"
            "   - If an explicit target goal is stated (e.g. 'I want to be a Data Scientist'), prioritize that target goal.\n\n"
            "3. Skill Ratings (0-5 Scale) across the 15 database skills:\n"
            "   'Excel', 'SQL', 'Python', 'Pandas', 'Statistics', 'Data Visualization', 'Power BI',\n"
            "   'Machine Learning', 'Deep Learning', 'HTML & CSS', 'JavaScript', 'React',\n"
            "   'Network Security', 'Ethical Hacking', 'Git'.\n"
            "   - 0: No knowledge, unmentioned, or explicitly negated\n"
            "   - 1: Beginner / Starting\n"
            "   - 2: Basic / Familiar / Know\n"
            "   - 3: Intermediate / Working Experience\n"
            "   - 4: Advanced / Proficient\n"
            "   - 5: Expert\n\n"
            "FEW-SHOT EXAMPLES:\n"
            "Example 1 Input: 'i know python,html'\n"
            "Example 1 Output: {\"target_career\": \"Web Developer\", \"experience_level\": \"Beginner\", \"study_hours_per_week\": 12.0, \"interests\": \"Web Development, HTML & CSS, Python\", \"career_summary\": \"Aspiring Web Developer with foundational knowledge in Python and HTML & CSS.\", \"learning_strategy\": \"Focus on modern JavaScript and React to bridge core frontend gaps.\", \"detected_skills\": {\"Excel\": 0, \"SQL\": 0, \"Python\": 2, \"Pandas\": 0, \"Statistics\": 0, \"Data Visualization\": 0, \"Power BI\": 0, \"Machine Learning\": 0, \"Deep Learning\": 0, \"HTML & CSS\": 2, \"JavaScript\": 0, \"React\": 0, \"Network Security\": 0, \"Ethical Hacking\": 0, \"Git\": 0}}\n\n"
            "Example 2 Input: 'i have ethical hacking and wireshark background'\n"
            "Example 2 Output: {\"target_career\": \"Cybersecurity Analyst\", \"experience_level\": \"Intermediate\", \"study_hours_per_week\": 12.0, \"interests\": \"Cybersecurity, Network Security, Ethical Hacking\", \"career_summary\": \"Cybersecurity enthusiast with hands-on ethical hacking and packet analysis skills.\", \"learning_strategy\": \"Prioritize network defense, OWASP audit frameworks, and security certifications.\", \"detected_skills\": {\"Excel\": 0, \"SQL\": 0, \"Python\": 0, \"Pandas\": 0, \"Statistics\": 0, \"Data Visualization\": 0, \"Power BI\": 0, \"Machine Learning\": 0, \"Deep Learning\": 0, \"HTML & CSS\": 0, \"JavaScript\": 0, \"React\": 0, \"Network Security\": 3, \"Ethical Hacking\": 3, \"Git\": 0}}"
        )

        # 1. First, attempt dynamic model discovery via ListModels API
        discovered_models = []
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            list_resp = requests.get(list_url, timeout=8)
            if list_resp.status_code == 200:
                models_data = list_resp.json().get("models", [])
                for m in models_data:
                    m_name = m.get("name", "")
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" in methods:
                        # Extract model identifier, e.g. "models/gemini-1.5-flash" -> "gemini-1.5-flash"
                        clean_m = m_name.replace("models/", "")
                        discovered_models.append(("v1beta", clean_m))
        except Exception:
            pass

        # 2. Add fallback model candidates in order of preference
        static_candidates = [
            ("v1beta", "gemini-1.5-flash"),
            ("v1beta", "gemini-1.5-flash-latest"),
            ("v1beta", "gemini-2.0-flash"),
            ("v1beta", "gemini-2.5-flash"),
            ("v1", "gemini-1.5-flash"),
            ("v1", "gemini-pro"),
            ("v1beta", "gemini-1.5-pro"),
            ("v1beta", "gemini-1.0-pro"),
        ]

        all_candidates = []
        # Add discovered models first
        for item in discovered_models:
            if item not in all_candidates:
                all_candidates.append(item)
        # Append static candidates
        for item in static_candidates:
            if item not in all_candidates:
                all_candidates.append(item)

        last_error = ""

        for version, model in all_candidates:
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_instruction}\n\nAnalyze this user profile and output JSON strictly conforming to the schema:\n{user_text}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                    "max_output_tokens": 1000
                }
            }

            if version == "v1beta":
                payload["system_instruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            try:
                response = requests.post(url, json=payload, timeout=12)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
                        raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                        raw_text = re.sub(r"\n?```$", "", raw_text)
                        return json.loads(raw_text)
                elif response.status_code == 404:
                    last_error = f"Model {model} ({version}) not found."
                    continue
                else:
                    last_error = f"Status {response.status_code}: {response.text}"
            except Exception as e:
                last_error = str(e)
                continue

        raise RuntimeError(
            f"Google Gemini API could not generate content. Last error: {last_error}\n"
            "Tip: Ensure your API key is created at https://aistudio.google.com/app/apikey with the Google Generative Language API enabled."
        )

    def _validate_profile_structure(self, profile: Dict[str, Any]) -> bool:
        """Ensure LLM response complies with all required schema fields."""
        required_keys = ["target_career", "experience_level", "study_hours_per_week", "detected_skills"]
        if not all(k in profile for k in required_keys):
            return False
        if profile["target_career"] not in SUPPORTED_CAREERS:
            # Attempt to normalize
            for c in SUPPORTED_CAREERS:
                if c.lower() in str(profile["target_career"]).lower():
                    profile["target_career"] = c
                    break
        if not isinstance(profile.get("detected_skills"), dict):
            return False
        return True

    def _get_default_profile(self) -> Dict[str, Any]:
        """Fallback default profile."""
        return {
            "target_career": "Data Analyst",
            "experience_level": "Beginner",
            "study_hours_per_week": 12.0,
            "interests": "Data Analysis, Python, SQL",
            "career_summary": "Active learner preparing for career advancement.",
            "learning_strategy": "Establish core competency baselines in SQL and Python.",
            "detected_skills": {"Excel": 2, "SQL": 1, "Python": 0, "Pandas": 0, "Statistics": 0},
            "source": "Default Baseline"
        }

    @staticmethod
    def generate_course_explanation(course: Dict[str, Any], user_skills: Dict[int, int], career_reqs: List[Dict[str, Any]], user_profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate intelligent rationale explaining why a specific course is recommended.
        Analyzes exact current skill level vs target required level and importance.
        """
        skill_id = course.get("skill_id")
        skill_name = course.get("skill_name", "General Skill")
        current_lvl = user_skills.get(skill_id, 0)
        
        # Find requirement in career matrix
        req = next((r for r in career_reqs if r.get("skill_id") == skill_id), None)
        target_lvl = req.get("required_level", 3) if req else 3
        importance = req.get("importance", 0.8) if req else 0.8
        gap = max(0, target_lvl - current_lvl)

        course_diff = course.get("difficulty", 2)
        diff_label = "Beginner" if course_diff == 1 else "Intermediate" if course_diff == 2 else "Advanced"

        importance_pct = int(importance * 100)

        if gap > 0:
            if current_lvl == 0:
                return (
                    f"🔥 <strong>High Priority Gap (Importance: {importance_pct}%)</strong>: You currently have no logged foundation in <strong>{skill_name}</strong>. "
                    f"This {diff_label} course builds your baseline up to Level {min(target_lvl, course_diff)} required for your target role."
                )
            else:
                return (
                    f"⚡ <strong>Level Upgrade</strong>: Your current proficiency in <strong>{skill_name}</strong> is Level {current_lvl} (Target: Level {target_lvl}). "
                    f"This course closes {min(gap, 2)} gap unit(s) with practical hands-on exercises."
                )
        else:
            return (
                f"✨ <strong>Mastery & Benchmark Retention</strong>: You have met the minimum benchmark for <strong>{skill_name}</strong> (Level {current_lvl}/{target_lvl}). "
                f"This {diff_label} module reinforces advanced best practices and interview preparation."
            )

    @staticmethod
    def generate_curriculum_strategy(selected_career: str, df_skills: Any, study_hours: float) -> str:
        """Generate high-level strategic overview of the recommended learning sequence."""
        if hasattr(df_skills, "empty") and df_skills.empty:
            return f"Follow the sequential curriculum below to reach industry benchmark readiness for <strong>{selected_career}</strong>."

        try:
            high_gaps = df_skills[df_skills["Gap"] > 0].sort_values(by=["Importance", "Gap"], ascending=[False, False])
            if len(high_gaps) > 0:
                top_skill = high_gaps.iloc[0]["Skill"]
                top_gap = high_gaps.iloc[0]["Gap"]
                return (
                    f"💡 <strong>AI Strategy for {selected_career}</strong>: Highest ROI is currently in <strong>{top_skill}</strong> (Gap: {top_gap} levels). "
                    f"Dedicate ~{min(study_hours, 6.0):.0f} hours/week to top-priority modules below to accelerate your Career Readiness score by ~15-20%."
                )
            else:
                return f"🎉 <strong>Target Competency Benchmarks Met!</strong> Focus on Capstone Projects to build proof-of-work portfolio deliverables."
        except Exception:
            return f"Follow the personalized sequence below to systematically close skill gaps for <strong>{selected_career}</strong>."

    def generate_diagnostic_quiz(
        self,
        target_career: str,
        skills_list: List[str],
        user_background: str = "",
        custom_api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate 3-5 multiple-choice diagnostic questions to evaluate the user's
        true competency based on what they provided, avoiding manual estimation.
        """
        active_key = (custom_api_key or self.api_key or os.getenv("GEMINI_API_KEY", "")).strip()
        selected_skills = [s for s in skills_list if s]
        if not selected_skills:
            selected_skills = ["Python", "SQL", "Git"]

        # Limit to 3-5 skills to keep assessment fast (2-3 mins)
        target_eval_skills = selected_skills[:5]

        # 1. Try Live Gemini Generation if key available
        if active_key and len(active_key) > 8:
            try:
                ai_quiz = self._call_gemini_quiz_generation(target_career, target_eval_skills, user_background, active_key)
                if ai_quiz and len(ai_quiz) >= 3:
                    return ai_quiz
            except Exception:
                pass  # Graceful fallback to verified diagnostic repository

        # 2. Curated Built-in Diagnostic Question Repository
        return self._get_fallback_diagnostic_quiz(target_eval_skills, target_career)

    def _call_gemini_quiz_generation(
        self,
        target_career: str,
        skills: List[str],
        user_background: str,
        api_key: str
    ) -> List[Dict[str, Any]]:
        """Query Gemini to generate 3-5 customized practical diagnostic MCQs."""
        system_instruction = (
            "You are an expert technical interviewer for CareerPath AI.\n"
            f"Generate exactly {min(len(skills), 5)} multiple choice diagnostic questions to evaluate a candidate targeting '{target_career}'.\n"
            f"Candidate background: '{user_background}'.\n"
            f"Test these specific skills: {', '.join(skills)}.\n\n"
            "OUTPUT JSON SCHEMA:\n"
            "[\n"
            "  {\n"
            '    "id": 1,\n'
            '    "skill": "Skill Name",\n'
            '    "question": "Clear practical scenario or conceptual question",\n'
            '    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],\n'
            '    "correct_index": 0,\n'
            '    "explanation": "Why this answer is correct and what concept it tests",\n'
            '    "target_level": 3\n'
            "  }\n"
            "]"
        )

        models_to_try = [
            ("v1beta", "gemini-1.5-flash"),
            ("v1beta", "gemini-2.0-flash"),
            ("v1beta", "gemini-1.5-pro"),
            ("v1", "gemini-1.5-flash"),
        ]

        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"Generate diagnostic questions for skills: {', '.join(skills)}."}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
                "max_output_tokens": 1500
            },
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            }
        }

        for version, model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"
            try:
                resp = requests.post(url, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
                        raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                        raw_text = re.sub(r"\n?```$", "", raw_text)
                        parsed = json.loads(raw_text)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            for idx, q in enumerate(parsed):
                                q["id"] = idx + 1
                                if "correct_index" not in q or not (0 <= q["correct_index"] < len(q.get("options", []))):
                                    q["correct_index"] = 0
                            return parsed
            except Exception:
                continue

        return []

    def _get_fallback_diagnostic_quiz(self, skills: List[str], target_career: str) -> List[Dict[str, Any]]:
        """Verified offline diagnostic question bank covering all core skills."""
        bank = {
            "HTML & CSS": {
                "skill": "HTML & CSS",
                "question": "Which CSS layout method is best suited for 2-dimensional layouts (both rows and columns simultaneously)?",
                "options": ["A) CSS Grid", "B) Flexbox", "C) Float and Clearfix", "D) Inline-Block with Margins"],
                "correct_index": 0,
                "explanation": "CSS Grid is inherently designed for two-dimensional grid layouts (rows + columns), whereas Flexbox is primarily one-dimensional.",
                "target_level": 3
            },
            "JavaScript": {
                "skill": "JavaScript",
                "question": "In modern JavaScript (ES6+), what is the difference between `let` and `const`?",
                "options": [
                    "A) `let` is function-scoped while `const` is globally scoped",
                    "B) `const` variables cannot be reassigned after declaration, while `let` variables can",
                    "C) `const` makes objects completely immutable including their properties",
                    "D) `let` is hoisted to the top but `const` is not"
                ],
                "correct_index": 1,
                "explanation": "`const` prevents identifier reassignment (though internal object properties can still mutate). `let` allows variable reassignment in block scope.",
                "target_level": 3
            },
            "React": {
                "skill": "React",
                "question": "Why is the `key` prop required when rendering lists of elements in React?",
                "options": [
                    "A) It applies CSS styling uniquely to each list item",
                    "B) It helps React's Virtual DOM identify which items have changed, added, or removed for efficient re-renders",
                    "C) It automatically binds state variables to database rows",
                    "D) It prevents duplicate DOM element clicks"
                ],
                "correct_index": 1,
                "explanation": "React uses the `key` prop during reconciliation to differentiate items across re-renders without destroying and recreating unchanged DOM elements.",
                "target_level": 3
            },
            "Git": {
                "skill": "Git",
                "question": "Which Git command is used to integrate changes from one branch into another by reapplying commits on top of the base tip?",
                "options": ["A) git rebase", "B) git merge --no-ff", "C) git cherry-pick -a", "D) git checkout -b"],
                "correct_index": 0,
                "explanation": "`git rebase` rewrites commit history by moving or reapplying the base of your branch to another commit.",
                "target_level": 3
            },
            "Python": {
                "skill": "Python",
                "question": "What is the time complexity of looking up a key in a standard Python dictionary `dict`?",
                "options": ["A) O(1) Average Time", "B) O(n) Linear Time", "C) O(log n) Logarithmic Time", "D) O(n^2) Quadratic Time"],
                "correct_index": 0,
                "explanation": "Python dictionaries are implemented via hash tables, offering O(1) average time complexity for lookups, insertions, and deletions.",
                "target_level": 3
            },
            "SQL": {
                "skill": "SQL",
                "question": "What is the key difference between `WHERE` and `HAVING` clauses in SQL?",
                "options": [
                    "A) `WHERE` filters rows before aggregation; `HAVING` filters aggregated groups after `GROUP BY`",
                    "B) `HAVING` works only with indexed primary keys",
                    "C) `WHERE` cannot be used with `JOIN` operations",
                    "D) `HAVING` runs before `FROM` execution"
                ],
                "correct_index": 0,
                "explanation": "`WHERE` filters individual records prior to grouping. `HAVING` filters grouped summary values resulting from aggregate functions (e.g. `COUNT()`, `AVG()`).",
                "target_level": 3
            },
            "Excel": {
                "skill": "Excel",
                "question": "Which modern Excel function replaces both `VLOOKUP` and `INDEX(MATCH)` with bidirectional lookup capabilities?",
                "options": ["A) XLOOKUP", "B) HLOOKUP", "C) LOOKUP_EXACT", "D) SEARCH_ROW"],
                "correct_index": 0,
                "explanation": "`XLOOKUP` allows searching in any direction (left/right/vertical/horizontal) without column index numbers and defaults to exact matches.",
                "target_level": 3
            },
            "Pandas": {
                "skill": "Pandas",
                "question": "In Pandas, which method is used to aggregate data by multiple categories and calculate summary statistics?",
                "options": ["A) df.groupby().agg()", "B) df.pivot_filter()", "C) df.merge_categories()", "D) df.resample_columns()"],
                "correct_index": 0,
                "explanation": "`groupby()` combined with `agg()` allows flexible splitting, applying summary metrics (mean, sum, count), and combining results.",
                "target_level": 3
            },
            "Statistics": {
                "skill": "Statistics",
                "question": "When data is heavily skewed with extreme outliers, which measure of central tendency is the most robust?",
                "options": ["A) Median", "B) Mean (Arithmetic Average)", "C) Standard Deviation", "D) Mid-Range"],
                "correct_index": 0,
                "explanation": "The Median is resistant to outliers because it reflects the 50th percentile rank rather than taking the numerical sum of extreme values.",
                "target_level": 3
            },
            "Data Visualization": {
                "skill": "Data Visualization",
                "question": "Which chart type is most effective for displaying the distribution and spread of continuous numerical data across quartiles?",
                "options": ["A) Box Plot (Box-and-Whisker)", "B) Pie Chart", "C) Donut Chart", "D) Gauge Chart"],
                "correct_index": 0,
                "explanation": "Box Plots clearly show the median, interquartile range (IQR), minimum, maximum, and potential outliers in a single visual.",
                "target_level": 3
            },
            "Power BI": {
                "skill": "Power BI",
                "question": "In Power BI, what language is used to create dynamic custom calculated measures and columns?",
                "options": ["A) DAX (Data Analysis Expressions)", "B) M Language", "C) VBA Script", "D) Transact-SQL"],
                "correct_index": 0,
                "explanation": "DAX is the formula and query expression language used for defining calculations and measures in Power BI and Analysis Services.",
                "target_level": 3
            },
            "Machine Learning": {
                "skill": "Machine Learning",
                "question": "What common issue occurs when a machine learning model scores 99% accuracy on training data but performs poorly on unseen test data?",
                "options": ["A) Overfitting (High Variance)", "B) Underfitting (High Bias)", "C) Data Imbalance", "D) Learning Rate Decay"],
                "correct_index": 0,
                "explanation": "Overfitting occurs when a model memorizes noise and specific patterns in the training data, failing to generalize to new data.",
                "target_level": 3
            },
            "Deep Learning": {
                "skill": "Deep Learning",
                "question": "Which architectural component enables Transformer models to process all tokens in a sequence concurrently while capturing word relationships?",
                "options": ["A) Multi-Head Self-Attention Mechanism", "B) Recurrent Hidden Cell State", "C) Max Pooling Layer", "D) Convolutional Kernel Filter"],
                "correct_index": 0,
                "explanation": "Self-attention computes dynamic attention weights between all token pairs simultaneously, eliminating sequential RNN bottlenecks.",
                "target_level": 3
            },
            "Network Security": {
                "skill": "Network Security",
                "question": "What is the primary function of a Stateful Inspection Firewall compared to a basic Packet Filter?",
                "options": [
                    "A) It tracks the state of active network connections and dynamically validates whether incoming packets match established flows",
                    "B) It encrypts all network packets using SSL/TLS",
                    "C) It automatically assigns static IP addresses",
                    "D) It prevents physical ethernet cable disconnections"
                ],
                "correct_index": 0,
                "explanation": "Stateful firewalls maintain connection tables to evaluate whether a packet is part of an existing valid session, rather than inspecting headers in isolation.",
                "target_level": 3
            },
            "Ethical Hacking": {
                "skill": "Ethical Hacking",
                "question": "What security practice prevents SQL Injection vulnerabilities in database-driven web applications?",
                "options": [
                    "A) Parameterized Queries (Prepared Statements)",
                    "B) Client-side JavaScript length checking",
                    "C) Hashing database table names",
                    "D) Disabling HTTP port 80"
                ],
                "correct_index": 0,
                "explanation": "Parameterized queries separate SQL code from user-supplied data inputs, preventing malicious user input from altering query structure.",
                "target_level": 3
            }
        }

        quiz = []
        q_id = 1
        for s in skills:
            if s in bank:
                item = dict(bank[s])
                item["id"] = q_id
                quiz.append(item)
                q_id += 1

        # Fill with core fallbacks if fewer than 3
        if len(quiz) < 3:
            for s, item in bank.items():
                if item["skill"] not in [q["skill"] for q in quiz]:
                    q_copy = dict(item)
                    q_copy["id"] = q_id
                    quiz.append(q_copy)
                    q_id += 1
                    if len(quiz) >= 4:
                        break

        return quiz[:5]

    def evaluate_diagnostic_quiz(
        self,
        questions: List[Dict[str, Any]],
        user_answers: Dict[int, int],
        target_skills: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate candidate diagnostic answers and determine objective verified skill proficiency (0-5).
        """
        if target_skills is None:
            target_skills = {}

        total_questions = len(questions)
        correct_count = 0
        skill_evaluations = {}
        verified_skills = dict(target_skills)

        for q in questions:
            q_id = q.get("id", 1)
            skill = q.get("skill", "General")
            correct_idx = q.get("correct_index", 0)
            user_choice = user_answers.get(q_id, -1)
            target_lvl = q.get("target_level", 3)

            is_correct = (user_choice == correct_idx)
            if is_correct:
                correct_count += 1
                # Assign verified level based on question difficulty
                assessed_level = target_lvl
                status_label = "✅ Verified Competent"
            else:
                # Skill gap detected: level 0 or 1
                assessed_level = 1 if user_choice != -1 else 0
                status_label = "⚠️ Gap Identified"

            verified_skills[skill] = assessed_level
            user_opt_text = q["options"][user_choice] if (0 <= user_choice < len(q.get("options", []))) else "No Answer"
            correct_opt_text = q["options"][correct_idx] if (0 <= correct_idx < len(q.get("options", []))) else ""

            skill_evaluations[skill] = {
                "question": q.get("question", ""),
                "is_correct": is_correct,
                "user_answer": user_opt_text,
                "correct_answer": correct_opt_text,
                "explanation": q.get("explanation", ""),
                "assessed_level": assessed_level,
                "status": status_label
            }

        score_pct = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0

        return {
            "score_pct": score_pct,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "verified_skills": verified_skills,
            "skill_evaluations": skill_evaluations
        }

