import csv
import os

courses_data = [
    # Skill 1: Excel (1-4)
    (1, "Excel for Beginners: Data Entry & Formulas", "Master basic spreadsheet tools formatting and sum average functions.", 1, 1, "[]", 4.0, "Course", "Coursera", "https://coursera.org/learn/excel-basics", 4.7, "excel spreadsheet formulas beginner"),
    (2, "Intermediate Excel: VLOOKUP & Pivot Tables", "Learn VLOOKUP XLOOKUP Index-Match and dynamic pivot tables for data analysis.", 1, 2, "[1]", 6.0, "Course", "Udemy", "https://udemy.com/course/excel-vlookup-pivot", 4.8, "excel vlookup pivot-tables intermediate"),
    (3, "Advanced Excel: Dashboards & Data Analytics", "Build interactive executive dashboards using advanced formulas slicers and conditional formatting.", 1, 3, "[2]", 8.0, "Course", "LinkedIn Learning", "https://linkedin.com/learning/excel-dashboards", 4.6, "excel dashboards analytics advanced"),
    (4, "Excel Data Cleaning & Wrangling", "Learn techniques to sanitize messy datasets remove duplicates and split text columns.", 1, 2, "[1]", 3.0, "Tutorial", "YouTube", "https://youtube.com/watch?v=excel-cleaning", 4.5, "excel data-cleaning tutorial"),

    # Skill 2: SQL (5-9)
    (5, "SQL Basics: Querying Relational Databases", "Understand database tables SELECT WHERE GROUP BY ORDER BY and aggregation.", 2, 1, "[]", 5.0, "Course", "Codecademy", "https://codecademy.com/learn/learn-sql", 4.9, "sql databases queries beginner"),
    (6, "SQL Joins & Complex Queries Masterclass", "Master INNER JOIN LEFT JOIN Subqueries UNION and CTE window functions.", 2, 2, "[5]", 7.0, "Course", "Udemy", "https://udemy.com/course/sql-joins-masterclass", 4.8, "sql joins window-functions intermediate"),
    (7, "Advanced Database Design & SQL Optimization", "Learn indexing query optimization normalization and stored procedures.", 2, 3, "[6]", 10.0, "Course", "Coursera", "https://coursera.org/learn/database-optimization", 4.7, "sql indexing optimization advanced"),
    (8, "SQL Window Functions in 60 Minutes", "Quick video tutorial covering ROW_NUMBER RANK DENSE_RANK and LAG LEAD functions.", 2, 2, "[5]", 1.5, "Video", "YouTube", "https://youtube.com/watch?v=sql-window-func", 4.9, "sql window-functions video"),
    (9, "SQL Practice Problems & Interview Prep", "Interactive SQL exercises for practicing real-world data analyst interview queries.", 2, 2, "[6]", 4.0, "Quiz", "DataCamp", "https://datacamp.com/courses/sql-practice", 4.6, "sql practice interview"),

    # Skill 3: Python (10-14)
    (10, "Python Programming for Beginners", "Learn variables loops functions data structures and basic scripting in Python.", 3, 1, "[]", 8.0, "Course", "freeCodeCamp", "https://freecodecamp.org/learn/python-basics", 4.9, "python programming basics beginner"),
    (11, "Intermediate Python: Data Structures & OOP", "Master Object-Oriented Programming list comprehensions modules and file I/O.", 3, 2, "[10]", 10.0, "Course", "Udemy", "https://udemy.com/course/python-intermediate", 4.7, "python oop data-structures intermediate"),
    (12, "Python Automation & Scripting", "Build scripts to automate file management web scraping and data processing.", 3, 2, "[10]", 6.0, "Course", "Coursera", "https://coursera.org/learn/python-scripting", 4.8, "python automation scripting"),
    (13, "Python Functions & Lambda Expressions Tutorial", "Deep dive into clean Python functions kwargs args and map filter lambda.", 3, 2, "[10]", 2.0, "Tutorial", "RealPython", "https://realpython.com/python-lambda", 4.9, "python functions lambda tutorial"),
    (14, "Python Code Refactoring & Best Practices", "Learn PEP 8 standards clean code patterns type hinting and docstrings.", 3, 3, "[11]", 4.0, "Documentation", "Python Docs", "https://docs.python.org/3/tutorial", 4.6, "python best-practices pep8"),

    # Skill 4: Pandas (15-18)
    (15, "Pandas Fundamentals for Data Analysis", "Learn DataFrames Series data loading filtering and summary statistics.", 4, 2, "[10]", 6.0, "Course", "Kaggle", "https://kaggle.com/learn/pandas", 4.8, "pandas dataframe python data-analysis"),
    (16, "Data Manipulation & Cleaning with Pandas", "Master handling missing values groupby merging dataframes and apply functions.", 4, 2, "[15]", 7.0, "Course", "DataCamp", "https://datacamp.com/courses/pandas-data-manipulation", 4.7, "pandas data-cleaning groupby"),
    (17, "Advanced Pandas: Performance & Vectorization", "Optimize Pandas operations avoid slow loops use Categorical types and memory tuning.", 4, 3, "[16]", 5.0, "Course", "Udemy", "https://udemy.com/course/advanced-pandas", 4.6, "pandas optimization vectorization"),
    (18, "Pandas Cheat Sheet Walkthrough", "Comprehensive walkthrough of essential Pandas methods for fast lookup.", 4, 1, "[10]", 1.5, "Video", "YouTube", "https://youtube.com/watch?v=pandas-cheat-sheet", 4.8, "pandas video cheatsheet"),

    # Skill 5: Statistics (19-22)
    (19, "Introductory Statistics for Data Science", "Learn mean median standard deviation probability distributions and z-scores.", 5, 1, "[]", 6.0, "Course", "Khan Academy", "https://khanacademy.org/math/statistics", 4.9, "statistics probability basic math"),
    (20, "Inferential Statistics & Hypothesis Testing", "Master p-values confidence intervals t-tests ANOVA and chi-square tests.", 5, 2, "[19]", 8.0, "Course", "Coursera", "https://coursera.org/learn/inferential-stats", 4.7, "statistics hypothesis-testing p-value"),
    (21, "Applied Regression & Correlation Analysis", "Learn linear regression multiple regression log transformation and correlation metrics.", 5, 3, "[20]", 7.0, "Course", "edX", "https://edx.org/course/regression-analysis", 4.6, "statistics regression correlation"),
    (22, "Probability Theory & Bayes Theorem", "Clear guide to conditional probability Bayes rule and random variables.", 5, 2, "[19]", 3.0, "Tutorial", "3Blue1Brown", "https://youtube.com/watch?v=bayes-theorem", 5.0, "statistics bayes probability video"),

    # Skill 6: Data Visualization (23-26)
    (23, "Data Visualization with Matplotlib & Seaborn", "Create line plots bar charts histograms scatter plots and heatmaps in Python.", 6, 2, "[15]", 5.0, "Course", "Udemy", "https://udemy.com/course/matplotlib-seaborn", 4.7, "visualization matplotlib seaborn python"),
    (24, "Interactive Dashboards with Plotly & Dash", "Build interactive browser visualizations sliders tooltips and web dashboards.", 6, 3, "[23]", 8.0, "Course", "Coursera", "https://coursera.org/learn/plotly-dashboards", 4.8, "visualization plotly interactive dash"),
    (25, "Data Storytelling & Chart Choice Best Practices", "Learn visual hierarchy color theory chart selection and presentation skills.", 6, 1, "[]", 3.0, "Course", "LinkedIn Learning", "https://linkedin.com/learning/data-storytelling", 4.6, "visualization storytelling chart-design"),
    (26, "Seaborn Customization Guide", "Tutorial on styling color palettes facets and pairplots in Seaborn.", 6, 2, "[23]", 2.0, "Documentation", "Seaborn PyData", "https://seaborn.pydata.org/tutorial.html", 4.7, "visualization seaborn documentation"),

    # Skill 7: Power BI (27-30)
    (27, "Power BI Desktop Beginner to Pro", "Connect data sources build data models construct reports and publish dashboards.", 7, 1, "[]", 8.0, "Course", "Udemy", "https://udemy.com/course/power-bi-beginner-to-pro", 4.8, "powerbi bi dashboards desktop"),
    (28, "DAX Formulas & Data Modeling in Power BI", "Master Data Analysis Expressions DAX measures calculated columns and relationships.", 7, 2, "[27]", 9.0, "Course", "Coursera", "https://coursera.org/learn/powerbi-dax", 4.7, "powerbi dax data-modeling"),
    (29, "Power BI Advanced Analytics & Service", "Learn Power BI Service scheduled refresh row-level security and DAX patterns.", 7, 3, "[28]", 6.0, "Course", "Pluralsight", "https://pluralsight.com/courses/powerbi-advanced", 4.5, "powerbi advanced security dax"),
    (30, "Power BI Quickstart Tutorial", "Get started with your first Power BI report in 30 minutes.", 7, 1, "[]", 0.5, "Video", "YouTube", "https://youtube.com/watch?v=powerbi-quickstart", 4.7, "powerbi video quickstart"),

    # Skill 8: Machine Learning (31-35)
    (31, "Machine Learning Specialization by Andrew Ng", "Master supervised learning regression classification decision trees and evaluation metrics.", 8, 2, "[10, 15, 19]", 20.0, "Course", "Coursera", "https://coursera.org/specializations/machine-learning-introduction", 4.9, "ml machine-learning regression classification scikit-learn"),
    (32, "Applied Machine Learning with Scikit-Learn", "Practical ML pipeline creation feature engineering hyperparameter tuning and cross-validation.", 8, 3, "[31]", 12.0, "Course", "Udemy", "https://udemy.com/course/applied-ml-scikit", 4.8, "ml scikit-learn hyperparameters pipeline"),
    (33, "Unsupervised Learning & Clustering Algorithms", "Understand K-Means hierarchical clustering PCA dimensionality reduction and anomaly detection.", 8, 3, "[31]", 8.0, "Course", "edX", "https://edx.org/course/unsupervised-learning", 4.7, "ml kmeans pca clustering"),
    (34, "Machine Learning Evaluation Metrics Explained", "In-depth guide to Precision Recall F1 Score ROC-AUC curve and Confusion Matrix.", 8, 2, "[31]", 2.0, "Tutorial", "TowardsDataScience", "https://towardsdatascience.com/ml-metrics", 4.8, "ml metrics precision-recall tutorial"),
    (35, "Machine Learning Interview Practice Questions", "Top ML conceptual questions model selection overfitting bias-variance tradeoff.", 8, 3, "[32]", 3.0, "Quiz", "InterviewQuery", "https://interviewquery.com/ml-prep", 4.6, "ml quiz interview-prep"),

    # Skill 9: Deep Learning (36-39)
    (36, "Deep Learning & Neural Networks Foundations", "Understand forward propagation backpropagation activation functions and loss optimization.", 9, 3, "[31]", 15.0, "Course", "Coursera", "https://coursera.org/learn/neural-networks-deep-learning", 4.9, "deep-learning neural-networks pytorch tensorflow"),
    (37, "Convolutional Neural Networks for Computer Vision", "Build CNN architectures image classification object detection and transfer learning.", 9, 4, "[36]", 12.0, "Course", "Coursera", "https://coursera.org/learn/convolutional-neural-networks", 4.8, "deep-learning cnn computer-vision pytorch"),
    (38, "Natural Language Processing with Transformers", "Master RNNs LSTMs Attention mechanism BERT and HuggingFace Transformers.", 9, 4, "[36]", 14.0, "Course", "Udemy", "https://udemy.com/course/nlp-transformers", 4.7, "deep-learning nlp transformers huggingface"),
    (39, "PyTorch Quickstart for Deep Learning", "Hands-on guide to building tensors autograd neural network modules in PyTorch.", 9, 3, "[31]", 4.0, "Tutorial", "PyTorch Docs", "https://pytorch.org/tutorials/beginner/basics/intro.html", 4.9, "deep-learning pytorch tutorial"),

    # Skill 10: HTML & CSS (40-42)
    (40, "HTML5 & CSS3 Responsive Web Design", "Learn semantic HTML tags CSS flexbox CSS grid media queries and mobile layouts.", 10, 1, "[]", 6.0, "Course", "freeCodeCamp", "https://freecodecamp.org/learn/responsive-web-design", 4.9, "html css web-design flexbox grid"),
    (41, "Modern CSS Layouts & Animations", "Master CSS transitions keyframe animations TailwindCSS basics and modern layout utilities.", 10, 2, "[40]", 5.0, "Course", "Udemy", "https://udemy.com/course/modern-css-layouts", 4.7, "css flexbox grid animation tailwind"),
    (42, "HTML5 Semantic Tags & Accessibility", "Best practices for web accessibility ARIA roles SEO and semantic web structure.", 10, 1, "[]", 2.0, "Documentation", "MDN Web Docs", "https://developer.mozilla.org/docs/Web/HTML", 4.8, "html accessibility mdn documentation"),

    # Skill 11: JavaScript (43-45)
    (43, "JavaScript Basics for Beginners", "Learn variables data types arrays loops functions and DOM manipulation.", 11, 1, "[40]", 8.0, "Course", "Codecademy", "https://codecademy.com/learn/introduction-to-javascript", 4.8, "javascript js programming dom beginner"),
    (44, "Modern ES6+ JavaScript & Async Programming", "Master promises async await arrow functions destructuring modules and fetch API.", 11, 2, "[43]", 10.0, "Course", "Udemy", "https://udemy.com/course/modern-javascript-es6", 4.9, "javascript es6 async promises api"),
    (45, "JavaScript DOM Manipulation Crash Course", "Interactive tutorial building dynamic web pages by selecting and updating DOM nodes.", 11, 1, "[40]", 2.5, "Video", "YouTube", "https://youtube.com/watch?v=dom-manipulation", 4.8, "javascript dom video tutorial"),

    # Skill 12: React (46-48)
    (46, "React Fundamentals: Components & State", "Learn React functional components JSX props useState hook and event handling.", 12, 2, "[44]", 10.0, "Course", "React Official", "https://react.dev/learn", 4.9, "react frontend components hooks jsx"),
    (47, "Advanced React: useEffect Context & Redux", "Master side effects custom hooks context API global state management and routing.", 12, 3, "[46]", 12.0, "Course", "Udemy", "https://udemy.com/course/react-advanced-redux", 4.8, "react state-management hooks redux context"),
    (48, "React Hooks Cheatsheet & Patterns", "Quick reference guide to useState useEffect useMemo useCallback and useRef.", 12, 2, "[46]", 2.0, "Documentation", "React Docs", "https://react.dev/reference/react", 4.8, "react hooks documentation cheatsheet"),

    # Skill 13: Network Security (49-51)
    (49, "Computer Networking & Network Security Fundamentals", "Learn OSI model TCP/IP firewalls VPNs routers packet filtering and encryption.", 13, 1, "[]", 8.0, "Course", "Coursera", "https://coursera.org/learn/network-security-basics", 4.8, "networking security osi tcpip firewall"),
    (50, "Network Penetration Testing & Packet Analysis", "Master Wireshark Nmap network sniffing port scanning and traffic analysis.", 13, 2, "[49]", 10.0, "Course", "Cybrary", "https://cybrary.it/course/network-pentesting", 4.7, "networking wireshark nmap pentesting"),

    # Skill 14 & 15: Ethical Hacking & Git (51-53)
    (51, "Ethical Hacking & Vulnerability Assessment", "Learn system vulnerabilities exploitation basics OWASP Top 10 and security auditing.", 14, 2, "[49]", 12.0, "Course", "Udemy", "https://udemy.com/course/ethical-hacking-basics", 4.8, "hacking cybersecurity owasp vulnerabilities"),
    (52, "Git & GitHub Version Control Masterclass", "Master git init commit branch merge pull requests merge conflicts and GitHub workflows.", 15, 1, "[]", 4.0, "Course", "freeCodeCamp", "https://freecodecamp.org/learn/git-github", 4.9, "git github version-control workflow"),
    (53, "Git Branching Strategies & Team Workflows", "Learn Gitflow feature branching interactive rebase and pull request code reviews.", 15, 2, "[52]", 3.0, "Tutorial", "Atlassian Git", "https://atlassian.com/git/tutorials", 4.8, "git branching rebase workflow")
]

os.makedirs("c:/Users/Gokul/OneDrive/文档/hcl/data", exist_ok=True)
with open("c:/Users/Gokul/OneDrive/文档/hcl/data/courses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["course_id", "title", "description", "skill_id", "difficulty", "prerequisites", "duration_hours", "resource_type", "provider", "url", "rating", "tags"])
    for row in courses_data:
        writer.writerow(row)

print("Generated courses.csv successfully with", len(courses_data), "learning resources.")
