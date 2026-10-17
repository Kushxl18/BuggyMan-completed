# BuggyMan — Interactive AI-Powered Debugging Arena & Skill Evaluation Platform

> **Interview Preparation & Engineering Master Guide**  
> *This document is designed as a complete technical guide to help understand, demonstrate, and answer deep technical questions about the BuggyMan platform during software engineering interviews.*

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Explanation for Interviews](#2-project-explanation-for-interviews)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture & Data Flow](#4-system-architecture--data-flow)
5. [Feature-by-Feature Explanation](#5-feature-by-feature-explanation)
6. [Exact Code References](#6-exact-code-references)
7. [Important Code Deep Dive](#7-important-code-deep-dive)
8. [Database Design & Schema](#8-database-design--schema)
9. [API Documentation & HTTP Lifecycle](#9-api-documentation--http-lifecycle)
10. [Authentication, Authorization & Security](#10-authentication-authorization--security)
11. [Algorithms & Computational Complexity](#11-algorithms--computational-complexity)
12. [Error Handling & Resiliency](#12-error-handling--resiliency)
13. [Performance & Scalability Blueprint](#13-performance--scalability-blueprint)
14. [Testing Suite & Quality Assurance](#14-testing-suite--quality-assurance)
15. [Important Architectural & Design Decisions](#15-important-architectural--design-decisions)
16. [Real Engineering Challenges & Solutions](#16-real-engineering-challenges--solutions)
17. [System Limitations & Honest Trade-Offs](#17-system-limitations--honest-trade-offs)
18. [Production Readiness & Scalability Roadmap](#18-production-readiness--scalability-roadmap)
19. [Deployment & Environment Setup Guide](#19-deployment--environment-setup-guide)
20. [Complete File-by-File Codebase Directory](#20-complete-file-by-file-codebase-directory)
21. [Comprehensive Interview Question Bank](#21-comprehensive-interview-question-bank)
22. [Model Answers for Technical Interviews](#22-model-answers-for-technical-interviews)
23. [Live Demo Script & Walkthrough Guide](#23-live-demo-script--walkthrough-guide)
24. ["Show Me the Code" Quick-Reference Map](#24-show-me-the-code-quick-reference-map)
25. [Final Interview Cheat Sheet](#25-final-interview-cheat-sheet)

---

## 1. Project Overview

### Project Title
**BuggyMan — Interactive AI-Powered Debugging Arena & Skill Evaluation Platform**

### One-Line Description
A full-stack, gamified developer platform that evaluates software engineers through real-world bug-fixing challenges using an isolated multi-runtime evaluation engine, dynamic AI bug generation, and adaptive machine learning skill profiling.

### Problem Statement
Traditional coding platforms (LeetCode, HackerRank) focus heavily on algorithmic problem solving from scratch (e.g., reversing binary trees or dynamic programming). However, 70% to 80% of a real-world software engineer's daily work involves **reading existing codebases, diagnosing obscure bugs, understanding framework state mutations, and fixing broken SQL queries or CSS layouts**. Existing platforms do not adequately train or assess developers on these core debugging capabilities.

### Motivation
Developers need an environment that mirrors real software engineering: broken React hook state cycles, race conditions in Django async consumers, missing SQL `WHERE` clauses causing database table locks, and CSS flexbox/grid layout collapses. BuggyMan was created to bridge this gap by providing an interactive workspace where engineers fix realistic bugs, receive immediate automated test evaluation, and benefit from personalized ML-driven skill recommendations.

### Objectives
- **Realistic Debugging Workspaces**: Provide a browser-based IDE (Monaco Editor) pre-loaded with broken multi-file projects across React, Django, Python, SQL, and CSS.
- **Isolated Multi-Runtime Code Execution**: Safely execute user submissions against test suites across Python 3, Node.js, SQLite, and static Web runtimes.
- **Adaptive Machine Learning Recommendations**: Profile user skill vectors across technologies and categories to dynamically recommend challenges at the user's optimal learning boundary ($55\% - 78\%$ success probability).
- **Gamification & Analytics**: Incentivize progression via XP points, daily active streaks, achievement badges, tie-broken leaderboards, and interactive skill radar charts.
- **Admin & Moderation Suite**: Allow platform administrators to audit user submissions, create/publish/archive challenges, and manage security audit logs.

### Target Users
- **Software Developers & Computer Science Students**: Practicing real-world debugging, framework concepts, and database query optimization.
- **Technical Interviewees**: Preparing for practical debugging rounds and code inspection assessments.
- **Recruiters & Engineering Managers**: Evaluating candidates on actual code comprehension and debugging efficiency rather than abstract DSA puzzles.

### Key Features
1. **Interactive Multi-File Code Workspace IDE** with tabs, syntax highlighting, reset capabilities, and timer controls.
2. **Multi-Language Execution Engine** evaluating Python, JavaScript/React, SQL queries, and CSS/HTML layouts.
3. **Adaptive Machine Learning Engine** featuring `DifficultyPredictor`, `SkillProfiler`, `ChallengeRecommender`, and `WeaknessDetector`.
4. **Dynamic AI Challenge Generator & Bug Injector** producing context-aware debugging scenarios on demand.
5. **Specialized Arenas**:
   - **Code Challenges Arena**: Core algorithm, logic, and state management debugging.
   - **SQL Lab**: Interactive database schema querying, join optimization, and query fixes.
   - **Frontend Studio**: Micro-interactions, CSS Grid/Flexbox responsiveness, and visual UI debugging.
6. **Real-time Leaderboard & Tie-Breaking System** ordering players by XP, challenges solved, attempt count, and account age.
7. **Comprehensive User Analytics Dashboard** displaying skill radar charts, weekly time distribution, and weak spots.
8. **Admin Control Panel** for challenge moderation, user role elevation, and security audit log inspection.
9. **Observability & Security Auditing** with sensitive data sanitization, sliding-window rate limiting, and structured JSON event logging.

---

## 2. Project Explanation for Interviews

### 30-Second Explanation (Elevator Pitch)
> "BuggyMan is a full-stack developer platform designed to train and evaluate software engineers on real-world debugging rather than abstract DSA algorithms. It features a browser-based multi-file IDE built with React and Monaco Editor, backed by a Django REST API. Behind the scenes, a custom isolated execution engine runs user fixes against test suites across Python, Node.js, SQL, and Web runtimes. It also incorporates a machine learning layer that profiles user skills and dynamically recommends challenges tailored to each developer's proficiency level."

### 1-Minute Explanation (Standard Technical Pitch)
> "While traditional competitive programming sites ask candidates to write algorithms from scratch, BuggyMan evaluates how engineers solve real production issues—like React state mutation bugs, Django signal context errors, or un-indexed SQL queries. 
> 
> Architecturally, the frontend is built with React 18 and Vite, offering a dark/light responsive interface with Monaco Editor. The backend is powered by Django REST Framework. When a user submits code, our Evaluation Engine routes the files to dedicated runtime adapters (Python, Node.js, SQLite, or Static CSS), executes them inside isolated subprocess environments, evaluates test cases via regex and output parsing, and returns immediate diagnostic feedback. 
> 
> Furthermore, BuggyMan includes a machine learning engine that calculates a user's skill vector across technologies using exponentially weighted performance history. It predicts challenge success probability using a sigmoidal model and adapts recommended content to maintain optimal user engagement."

### 2–3 Minute Detailed Explanation (Deep Technical Overview)
> "BuggyMan was engineered to address a major gap in technical assessment: evaluating real-world debugging and code comprehension skills. 
> 
> On the frontend, we use React 18, React Router v6, and Tailwind CSS. The workspace IDE integrates Microsoft's Monaco Editor (`@monaco-editor/react`), supporting tabbed navigation across multi-file project structures, state persistence in `sessionStorage`, and real-time syntax checking.
> 
> On the backend, we built a modular architecture using Django REST Framework. The core engine is the `EvaluationEngine` in `backend/buggyman/evaluator/engine.py`. When code is executed, the engine dynamically resolves the correct runtime adapter (`PythonRuntimeAdapter`, `NodeRuntimeAdapter`, `SQLRuntimeAdapter`, or `StaticCodeRuntimeAdapter`). The adapter sanitizes inputs, injects setup schemas if needed (like SQL `schema.sql`), and delegates execution to `SubprocessSandboxRunner`. This runner executes code in isolated subprocesses with strict execution timeouts ($5.0\text{s}$) to prevent infinite loops or system resource exhaustion.
> 
> For user growth, we implemented a custom Machine Learning subsystem:
> 1. `SkillProfiler` (`backend/buggyman/ml/skill_profiler.py`): Calculates a $0-100$ skill score for every technology and category based on submission accuracy ($70\%$ weight) and problem volume ($30\%$ weight).
> 2. `DifficultyPredictor` (`backend/buggyman/ml/difficulty_predictor.py`): Uses a sigmoidal probability model ($P(success) = \frac{1}{1 + e^{-2.2 \cdot \Delta}}$) comparing user skill to numerical challenge difficulty.
> 3. `ChallengeRecommender` (`backend/buggyman/ml/recommender.py`): Scores unsolved challenges and surface items falling into the optimal learning zone ($55\% - 78\%$ probability).
> 
> Security and quality were prioritized: all authentication endpoints use custom JWT tokens and sliding-window rate limiters (`throttling.py`). Sensitive user data (passwords, tokens) is recursively scrubbed by `sanitize_data()` before hitting system loggers (`logger.py`). The application includes 78 automated unit and integration tests covering the entire workflow."

### Recommended Live Demonstration Sequence
1. **Authentication & Onboarding**: Show Login page $\rightarrow$ enter user credentials $\rightarrow$ authenticate and demonstrate JWT persistent session loading.
2. **Dashboard & ML Recommendations**: Highlight XP score, active daily streak, skill radar chart, and ML-recommended challenges tailored to the user's current skill profile.
3. **Debugging Arena (Code Challenges)**: Select Challenge ID 2 (`Search Bugs`) $\rightarrow$ open Monaco Editor workspace $\rightarrow$ inspect buggy state mutation code $\rightarrow$ click **Run Code** $\rightarrow$ show execution failure in Output Panel $\rightarrow$ fix code $\rightarrow$ click **Submit Solution** $\rightarrow$ transition to Result Page with awarded XP and streak update.
4. **Specialized Arenas**:
   - **SQL Lab**: Open `SQL-E01` $\rightarrow$ inspect `schema.sql` and `query.sql` $\rightarrow$ fix missing `WHERE` clause $\rightarrow$ execute.
   - **Frontend Studio**: Open `FE-E01` $\rightarrow$ inspect CSS flexbox properties $\rightarrow$ fix layout alignment.
5. **AI Challenge Generator**: Click **Generate Challenge** in the AI banner $\rightarrow$ trigger `AIChallengeGenerator` $\rightarrow$ show dynamically generated problem pre-loaded into workspace.
6. **Leaderboard**: Demonstrate global standings, rank badges, and tie-breaking ordering.
7. **Admin Dashboard**: Switch to Admin user $\rightarrow$ view system metrics, toggle challenge status (`published` / `archived`), and inspect security audit log entries.

---

## 3. Technology Stack

| Technology / Library | Layer | Purpose in BuggyMan | Why Chosen | Alternative Considered | Why Choice is Reasonable |
|---|---|---|---|---|---|
| **React 18** | Frontend Framework | Renders reactive SPA, component hierarchy, state hooks | Declarative UI, virtual DOM, massive ecosystem, hooks for state management | Vue.js / Angular | Industry standard for complex client-side applications with dynamic UI updates |
| **Vite** | Frontend Build Tool | Bundles JSX/CSS assets, hot module replacement (HMR) | Near-instant startup, fast ESM bundling speed | Webpack | Significantly faster dev build times and smaller production bundle sizes |
| **Tailwind CSS** | Styling Framework | Utility-first CSS styling, theme variable integration | Rapid UI development, responsive utilities, seamless dark mode | Styled Components / Bootstrap | Highly customizable, zero runtime CSS overhead, easy dark theme implementation |
| **Monaco Editor** | Code Editor Component | In-browser code editing engine (VS Code editor core) | Native syntax highlighting, line numbers, automatic layout | CodeMirror | Delivers authentic VS Code editing experience familiar to software engineers |
| **Django 5.0** | Backend Framework | Core REST API web framework, ORM database abstraction | Battery-included security, clean ORM, robust admin, native Python ML integration | Node.js (Express) / FastAPI | Simplifies database operations and seamlessly integrates Python ML/evaluator modules |
| **Django REST Framework (DRF)** | API Layer | Serializes models into JSON, manages HTTP request view handlers | Standard DRF decorators (`@api_view`), structured HTTP status responses | FastAPI / Flask-RESTful | Excellent integration with Django ORM, authentication decorators, and response utilities |
| **SQLite / PostgreSQL** | Database Engine | Relational storage for users, challenges, submissions, notifications | SQLite for lightweight local dev; PostgreSQL ready via Django ORM | MongoDB | Relational integrity is mandatory for linking Users $\leftrightarrow$ Submissions $\leftrightarrow$ Challenges |
| **PyJWT** | Authentication | Encodes and verifies JSON Web Tokens for stateless API auth | Stateless authorization, configurable expiration timestamps | Session Cookies | Enables decoupled frontend/backend deployment without server-side session storage |
| **Subprocess Execution (Python `subprocess`)** | Execution Sandbox | Spawns isolated shell processes for Python, Node, SQL runs | Process isolation, timeout enforcement (`timeout=5.0s`), stdout/stderr capture | Docker Containers / Pyodide | Lightweight, fast execution ($<100\text{ms}$ startup), zero external docker daemon dependency |
| **Recharts** | Data Visualization | Renders skill radar charts, time distribution bar charts | Declarative React SVG charting library, theme customizable | Chart.js | Native React integration without DOM manipulation hacks |
| **Lucide React** | Iconography | Renders crisp UI icons across dashboard, navbar, and panels | Clean SVG icons, tree-shakable, consistent design language | FontAwesome | Modern aesthetic, smaller bundle footprint |

---

## 4. System Architecture & Data Flow

### Architecture Diagram (Textual Representation)

```
+-----------------------------------------------------------------------------------+
|                                    BROWSER (CLIENT)                               |
|                                                                                   |
|   +-------------------+    +--------------------+    +------------------------+   |
|   |  Dashboard / Catalog|    |  Monaco IDE Workspace|    |  Analytics / Leaderboard|   |
|   +---------+---------+    +----------+---------+    +-----------+------------+   |
|             |                         |                          |                |
|             +-------------------------+--------------------------+                |
|                                       | (HTTP REST / JSON)                        |
+---------------------------------------|-------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|                                 DJANGO REST BACKEND                               |
|                                                                                   |
|  +--------------------+   +-----------------------+   +------------------------+  |
|  | JWT & Rate Limiter | ->|  Views / Controllers  | ->|  Observability Logger  |  |
|  |  (throttling.py)   |   |      (views.py)       |   |       (logger.py)      |  |
|  +--------------------+   +-----------+-----------+   +------------------------+  |
|                                       |                                           |
|         +-----------------------------+-----------------------------+             |
|         |                             |                             |             |
|         v                             v                             v             |
|  +--------------+            +-----------------+           +-------------------+  |
|  |  Django ORM  |            | Evaluation Engine|           | ML Subsystem      |  |
|  |  (models.py) |            |   (engine.py)   |           | (SkillProfiler,   |  |
|  +------+-------+            +--------+--------+           | DifficultyPredictor)|
|         |                             |                    +---------+---------+  |
|         |                             v                              |            |
|         |                    +-----------------+                     |            |
|         |                    | Runtime Adapters|                     |            |
|         |                    | (Python, Node,  |                     |            |
|         |                    |  SQL, Static)   |                     |            |
|         |                    +--------+--------+                     |            |
|         |                             |                              |            |
|         |                             v                              |            |
|         |                    +-----------------+                     |            |
|         |                    | Subprocess      |                     |            |
|         |                    | Sandbox Runner  |                     |            |
|         |                    +-----------------+                     |            |
|         |                                                            |            |
+---------|------------------------------------------------------------|------------+
          |                                                            |
          v                                                            v
+------------------+                                         +-------------------+
| SQLite / Postgres|                                         | Dynamic AI Engine |
| Database Storage |                                         | Generator/Injector|
+------------------+                                         +-------------------+
```

### Complete Request-Response Lifecycle Sequence

```
User -> Frontend IDE -> API Request -> Backend Views -> Business Logic -> Subprocess Sandbox / Database -> Response -> User UI

Detailed Step-by-Step Execution Flow:
1. User interacts with Monaco Editor in Frontend IDE (`EditorPage.jsx`) and clicks "Run Code" or "Submit Solution".
2. Frontend package constructs an API payload containing `{ code, files: [{ name, content }] }` and attaches `Authorization: Bearer <token>` header.
3. Request hits Django Backend URL Router (`urls.py`) and passes through `apply_rate_limit()` in `throttling.py` (sliding-window IP/User rate check).
4. View handler `submit_challenge_view()` in `views.py` decodes JWT token (`auth.py`) to resolve authenticated `User` object and fetches targeted `Challenge`.
5. View delegates code execution to `EvaluationEngine.evaluate()` in `backend/buggyman/evaluator/engine.py`.
6. `EvaluationEngine` resolves appropriate runtime adapter (`PythonRuntimeAdapter`, `NodeRuntimeAdapter`, `SQLRuntimeAdapter`, or `StaticCodeRuntimeAdapter`) based on challenge technology.
7. Adapter writes code files to temporary isolated directory, appends test runner wrappers, and invokes `SubprocessSandboxRunner.run_command()` with $5.0\text{s}$ timeout limit.
8. Subprocess sandbox executes code, captures `stdout`, `stderr`, exit code, and execution time.
9. Adapter parses test results, computes passed/failed counts, evaluates regex test criteria, and checks `bug_signature` detection.
10. Engine returns evaluation dictionary to `submit_challenge_view()`.
11. View updates `User` statistics (`total_score`, `challenges_solved`, `streak`), unlocks new `badges`, inserts user activity log item, and saves `Submission` record to database.
12. Backend returns HTTP 200 OK Response with score, test cases breakdown, execution time, and AI summary message.
13. Frontend receives JSON response, persists submission state to `sessionStorage`, updates global user state, displays toast notification, and navigates user to `ResultPage.jsx`.
```

---

## 5. Feature-by-Feature Explanation

### 1. Multi-File Workspace IDE & Code Editor
- **What it does**: Provides a browser-based IDE with Monaco Editor, file tabs, code resetting, timer tracking, and execution panels.
- **Why it exists**: Real software debugging requires navigating multiple project files (e.g. `App.jsx` + `styles.css` or `models.py` + `views.py`) rather than editing a single function stub.
- **How it works**: `EditorPage.jsx` manages workspace state (`files`, `activeFile`, `timeElapsed`), stores drafts in browser `sessionStorage`, and passes active file contents to `CodeEditor.jsx`.
- **Frontend File**: `frontend/src/pages/Challenge/EditorPage.jsx` (Lines 1–395) & `frontend/src/pages/Challenge/CodeEditor.jsx` (Lines 1–52).
- **Backend Endpoint**: `GET /api/challenges/:id` (`views.py:758-766`).
- **Edge Cases**: Empty file arrays, invalid file extensions, local `sessionStorage` corruption (handled via `normalizeFiles` fallback).

### 2. Multi-Language Execution & Evaluation Engine
- **What it does**: Safely executes user code across Python, JavaScript, SQL, and Web runtimes, returning test pass/fail results, `stdout`, `stderr`, and runtime benchmarks.
- **Why it exists**: Core infrastructure needed to evaluate whether a candidate's bug fix genuinely resolves targeted issues.
- **How it works**: `EvaluationEngine` (`engine.py`) inspects challenge technology and file extensions, resolves a runtime adapter (`runtimes.py`), and invokes `SubprocessSandboxRunner` (`sandboxes.py`) with a 5-second process timeout.
- **Backend File**: `backend/buggyman/evaluator/engine.py` (Lines 13–180).
- **Edge Cases**: Infinite loops (caught by process timeout), syntax crashes (stderr captured and returned gracefully), static CSS layout challenges (evaluated via string AST/regex verification).

### 3. Adaptive ML Skill Profiling & Recommendation
- **What it does**: Dynamically profiles user proficiency and recommends challenges at the candidate's optimal difficulty threshold.
- **Why it exists**: Keeps users engaged by preventing frustration (challenges too hard) or boredom (challenges too easy).
- **How it works**: `SkillProfiler` calculates technology skill vectors ($\text{Score} = 0.7 \cdot \text{Accuracy} + 0.3 \cdot \text{Volume}$). `DifficultyPredictor` calculates success probability using a sigmoid function ($P = \frac{1}{1 + e^{-2.2 \cdot \Delta}}$). `ChallengeRecommender` ranks unsolved challenges matching the target $55\% - 78\%$ probability window.
- **Backend Files**: `backend/buggyman/ml/skill_profiler.py` (Lines 9–95), `backend/buggyman/ml/difficulty_predictor.py` (Lines 9–96), `backend/buggyman/ml/recommender.py` (Lines 10–103).

### 4. Dynamic AI Challenge Generator & Bug Injector
- **What it does**: Generates fresh debugging challenges on demand with realistic code bugs, test cases, and suspected component flags.
- **Why it exists**: Provides unlimited practice content beyond the pre-seeded challenge catalog.
- **How it works**: `AIChallengeGenerator` constructs synthetic problem statements and starter code, runs `BugInjector` to introduce deliberate state/logic errors, validates the starter code fails, and saves the new challenge record to database.
- **Backend File**: `ai-engine/services/challenge_generator.py` & `views.py:1428-1481`.

### 5. Specialized SQL Lab Arena
- **What it does**: Interactive database debugging arena with pre-loaded `schema.sql` tables and broken `query.sql` files.
- **Why it exists**: Assesses SQL query writing, missing `WHERE` clauses, incorrect joins, and un-indexed schema constraints.
- **How it works**: `SQLRuntimeAdapter` creates an in-memory SQLite database process, executes `schema.sql` setup commands, executes the user's `query.sql`, compares returned dataset rows against `expected_query` results, and verifies constraints.
- **Frontend/Backend Files**: `frontend/src/pages/SQLChallenges.jsx` (Lines 1–336) & `backend/buggyman/evaluator/runtimes.py:180-260`.

### 6. Specialized Frontend Studio Arena
- **What it does**: Visual design arena focused on CSS Grid, Flexbox alignment, glassmorphism overlays, and animation layout shifts.
- **Why it exists**: Modern full-stack developers must debug complex client-side styling issues and responsive breakpoint collapses.
- **How it works**: Evaluated via `StaticCodeRuntimeAdapter` which parses CSS rules, checks required properties against test case expectations (e.g. `transition: background-color`), and reports visual compliance.
- **Frontend File**: `frontend/src/pages/FrontendDesignChallenges.jsx` (Lines 1–296).

### 7. Gamification, Badges & Leaderboard Tie-Breaking
- **What it does**: Tracks XP points, consecutive active streaks, achievement badges, and ranks users globally.
- **Why it exists**: Increases user retention through gamified progression.
- **How it works**: When a submission passes, `submit_challenge_view()` invokes `update_user_streak()` and `check_and_unlock_badges()`. Leaderboard query (`views.py:1260-1285`) breaks score ties by evaluating solved count, total attempts, and creation timestamp.
- **Backend File**: `backend/buggyman/views.py` (Lines 827–892 & 1260–1285).

### 8. User Analytics & Skill Radar Dashboard
- **What it does**: Displays visual radar charts of technology mastery, weekly activity bar charts, and category strength distribution.
- **Why it exists**: Gives developers clear feedback on their technical strengths and weak areas.
- **How it works**: `AnalyticsCollector.get_user_analytics_data()` aggregates submission logs, accuracy ratios, and time spent, returning structured datasets rendered by Recharts on the frontend.
- **Frontend/Backend Files**: `frontend/src/pages/Analytics.jsx` (Lines 1–260) & `backend/buggyman/ml/analytics_collector.py`.

### 9. Admin Dashboard & Content Moderation
- **What it does**: Enables administrators to review system metrics, manage user roles, publish or archive challenges, and inspect security logs.
- **Why it exists**: Essential for platform operations, content quality control, and auditing system safety.
- **How it works**: Protected by `is_admin_user(user)` checks (`views.py`). Admin endpoints (`admin_stats_view`, `admin_create_challenge_view`, `audit_log_list_view`) grant CRUD access to challenge statuses and audit logs.
- **Frontend/Backend Files**: `frontend/src/pages/AdminDashboard.jsx` (Lines 1–320) & `backend/buggyman/views.py:1310-1425`.

### 10. Observability, Security Logging & Sliding Rate Limiting
- **What it does**: Protects endpoints against brute-force attacks and logs structured events while scrubbing sensitive keys.
- **Why it exists**: Production systems require strict security throttling and audit trails.
- **How it works**: `apply_rate_limit()` in `throttling.py` uses Django cache sliding windows ($10\text{ req/min}$ for auth, $30\text{ req/min}$ for code execution). `sanitize_data()` in `logger.py` redacts passwords, tokens, and keys before JSON formatting.
- **Backend Files**: `backend/buggyman/throttling.py` (Lines 1–60) & `backend/buggyman/logger.py` (Lines 1–52).

---

## 6. Exact Code References

| Component / Feature | File Path | Class / Function Name | Line Range | Important Symbols / Variables | Purpose & Summary |
|---|---|---|---|---|---|
| **JWT Token Generation** | `backend/buggyman/auth.py` | `generate_jwt_token()` | L15–L35 | `jwt.encode`, `payload`, `SECRET_KEY` | Encodes user payload into signed JWT token with 7-day expiration |
| **Authentication Views** | `backend/buggyman/views.py` | `login_view()` / `register_view()` | L41–L105 | `check_password`, `validate_password` | Validates credentials, issues JWT token, and enforces rate limits |
| **Main Catalog Query** | `backend/buggyman/views.py` | `challenges_list_view()` | L193–L258 | `status='published'`, `SPECIAL_CHALLENGE_CATALOG` | Returns published challenges, excluding special arena prefixes for catalog |
| **Challenge Resolution** | `backend/buggyman/views.py` | `get_challenge_or_none()` | L720–L755 | `pk_str`, `alt_pk`, `FE-`/`RE-` | Resolves integer IDs, string aliases, and creates catalog items dynamically |
| **Execution Engine Core** | `backend/buggyman/evaluator/engine.py` | `EvaluationEngine.evaluate()` | L59–L180 | `resolve_adapter`, `norm_files`, `score` | Manages file normalization, adapter dispatch, execution timing, and scoring |
| **Subprocess Execution** | `backend/buggyman/evaluator/sandboxes.py` | `SubprocessSandboxRunner.run_command()` | L20–L65 | `subprocess.Popen`, `timeout=5.0`, `communicate` | Spawns isolated shell subprocess with strict execution timeout enforcement |
| **Python Runtime Adapter** | `backend/buggyman/evaluator/runtimes.py` | `PythonRuntimeAdapter.evaluate()` | L30–L95 | `ast.parse`, `unittest`, `tempfile` | Parses AST syntax, creates temporary test files, and executes Python tests |
| **Submission View Handler**| `backend/buggyman/views.py` | `submit_challenge_view()` | L894–L970 | `already_solved`, `update_user_streak` | Evaluates code, awards XP, unlocks badges, and persists submission record |
| **ML Skill Profiler** | `backend/buggyman/ml/skill_profiler.py` | `SkillProfiler.calculate_skill_matrix()`| L15–L85 | `tech_scores`, `cat_scores`, `vol_factor` | Computes $0-100$ skill vectors per technology and category |
| **ML Difficulty Predictor**| `backend/buggyman/ml/difficulty_predictor.py` | `DifficultyPredictor.predict_difficulty()`| L17–L95 | `delta`, `prob`, `math.exp(-2.2 * delta)` | Uses sigmoidal curve to predict user success probability |
| **ML Recommender** | `backend/buggyman/ml/recommender.py` | `ChallengeRecommender.get_recommendations()`| L12–L103 | `suitability_score`, `cache.set`, `tier_bonus` | Ranks unsolved challenges matching $55\%-78\%$ optimal learning zone |
| **Sliding Window Rate Limiter**| `backend/buggyman/throttling.py` | `apply_rate_limit()` | L15–L60 | `cache.get`, `timestamps`, `HTTP_429_TOO_MANY_REQUESTS` | Implements sliding-window cache rate limiting per IP/User |
| **Sensitive Data Sanitizer**| `backend/buggyman/logger.py` | `sanitize_data()` | L12–L26 | `SENSITIVE_KEYS`, `[REDACTED]` | Recursively redacts passwords, tokens, and keys before logging |
| **Frontend Router & Theme** | `frontend/src/App.jsx` | `App()` | L30–L150 | `setUser`, `theme`, `BrowserRouter` | Top-level React routing, authentication persistence, and dark/light theme |
| **IDE Workspace Manager** | `frontend/src/pages/Challenge/EditorPage.jsx` | `EditorPage()` | L54–L250 | `readPersistedWorkspace`, `handleRunCode` | Manages multi-file workspace state, timer, run, submit, and navigation |
| **Monaco Editor Component** | `frontend/src/pages/Challenge/CodeEditor.jsx` | `CodeEditor()` | L5–L50 | `Editor`, `getLanguage`, `vs-dark` | Integrates Monaco Editor with automatic syntax extension deduction |

---

## 7. Important Code Deep Dive

### Deep Dive 1: `EvaluationEngine.evaluate()`
**File**: `backend/buggyman/evaluator/engine.py` (Lines 59–180)

```python
def evaluate(self, challenge, files=None, code=None, timeout=5.0):
    start_time = time.time()
    
    # 1. Normalize challenge dictionary / model
    if hasattr(challenge, 'to_dict'):
        c_dict = challenge.to_dict()
        points = challenge.points
        technology = challenge.technology
        test_cases = challenge.test_cases or []
        bug_signature = challenge.bug_signature or ''
    # ...
    # 2. Normalize workspace files
    # ...
    # 3. Select appropriate runtime adapter
    adapter = self.resolve_adapter(technology, norm_files)

    # 4. Execute evaluation through adapter and sandbox runner
    res = adapter.evaluate(challenge, norm_files, test_cases, timeout=timeout)

    # 5. Process test results & backend score calculation
    test_results = res.get('test_results', [])
    tests_total = len(test_results)
    tests_passed = len([t for t in test_results if t.get('passed')])

    timed_out = res.get('timed_out', False)
    exit_code = res.get('exit_code', -1)
    error = res.get('error')

    if tests_total > 0:
        success = (tests_passed == tests_total) and not timed_out and (exit_code == 0 or adapter == self.static_adapter)
        score = int(round((tests_passed / tests_total) * points)) if success else 0
    else:
        success = (exit_code == 0) and not timed_out and not error
        score = points if success else 0
```

#### Detailed Breakdown
- **What it does**: Receives user code files, normalizes input shapes, resolves runtime adapters dynamically, executes sandboxed evaluation, and calculates score awarded.
- **Why written this way**: Polymorphic adapter pattern allows supporting diverse languages (Python, Node, SQL, CSS) without bloating the engine with language-specific execution logic.
- **Line-by-Line Logic**:
  - `Lines 63–80`: Normalizes input `challenge` whether passed as a Django `Challenge` ORM instance or a dictionary (vital for dynamic AI generated challenges).
  - `Lines 86–127`: Normalizes multi-file structures, ensuring secondary system files (like SQL `schema.sql`) are prepended if missing from user submissions.
  - `Line 130`: Calls `resolve_adapter()` to resolve the technology adapter (`PythonRuntimeAdapter`, `NodeRuntimeAdapter`, `SQLRuntimeAdapter`, `StaticCodeRuntimeAdapter`).
  - `Line 133`: Invokes `adapter.evaluate()` which delegates to `SubprocessSandboxRunner`.
  - `Lines 144–150`: Calculates score using all-or-nothing completion rules for test cases ($100\%$ test pass required for XP credit).
- **Time Complexity**: $\mathcal{O}(N + M)$ where $N$ is file count and $M$ is test case count (plus process execution runtime bounded by $5.0\text{s}$ timeout).
- **Space Complexity**: $\mathcal{O}(F)$ where $F$ is total size of workspace code files written to temp directory.
- **What happens if removed**: Code execution fails completely; users cannot run or submit code.

---

### Deep Dive 2: `DifficultyPredictor.predict_difficulty()`
**File**: `backend/buggyman/ml/difficulty_predictor.py` (Lines 17–95)

```python
# Skill delta equation
combined_skill = (user_tech_skill * 0.6) + (user_cat_skill * 0.4)
delta = (combined_skill - challenge_diff_val) / 35.0

# Sigmoid probability equation
prob = 1.0 / (1.0 + math.exp(-2.2 * delta))
```

#### Detailed Breakdown
- **What it does**: Computes mathematical probability ($0.0 - 1.0$) of a user successfully solving a given challenge based on their historical skill matrix.
- **Mathematical Formula**:
  $$\text{CombinedSkill} = 0.6 \cdot \text{Skill}_{\text{tech}} + 0.4 \cdot \text{Skill}_{\text{cat}}$$
  $$\delta = \frac{\text{CombinedSkill} - \text{Difficulty}_{\text{target}}}{35.0}$$
  $$P(\text{Success}) = \frac{1}{1 + e^{-2.2 \cdot \delta}}$$
- **Why written this way**: The sigmoid function maps arbitrary skill differences smoothly to a bounded $[0, 1]$ probability range, modeling human learning curves where small skill increments around matching difficulty yield significant probability gains.
- **Time Complexity**: $\mathcal{O}(S)$ where $S$ is user's submission history size.
- **Space Complexity**: $\mathcal{O}(1)$ auxiliary memory.

---

### Deep Dive 3: `submit_challenge_view()`
**File**: `backend/buggyman/views.py` (Lines 894–970)

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_challenge_view(request, pk):
    lim = apply_rate_limit(request, 'code_execution', limit=30)
    if lim:
        return lim
    challenge = get_challenge_or_none(pk)
    # ...
    eval_res = evaluation_engine.evaluate(challenge, files=files, code=code)
    is_success = eval_res['success']

    if is_success:
        if not already_solved:
            awarded_score = eval_res['score']
            user.challenges_solved += 1
            user.total_score += awarded_score

            update_user_streak(user)
            check_and_unlock_badges(user)
            # ...
```

#### Detailed Breakdown
- **What it does**: Handles atomic submission processing, invokes execution engine, updates user stats (`challenges_solved`, `total_score`), updates daily streak, evaluates achievement badges, and creates a immutable `Submission` log record.
- **Security Check**: Enforces $30\text{ requests/min}$ rate limit via `apply_rate_limit()`.
- **XP Crediting Rule**: Points are awarded **only on first successful solve** (`not already_solved`), preventing XP farming by submitting the same solution repeatedly.

---

## 8. Database Design & Schema

BuggyMan uses Django ORM configured with relational storage (SQLite for dev, PostgreSQL for production).

```
+-------------------+           +-----------------------+           +----------------------+
|       User        |           |      Submission       |           |      Challenge       |
+-------------------+           +-----------------------+           +----------------------+
| id (PK)           |<---------1| id (PK)               |1--------->| id (PK)              |
| username          |           | user_id (FK)          |           | title                |
| email             |           | challenge_id (FK)     |           | description          |
| password          |           | submitted_code        |           | status ('published') |
| role ('user')     |           | success (Bool)        |           | difficulty           |
| total_score (Int) |           | score (Int)           |           | technology           |
| challenges_solved |           | execution_time        |           | category             |
| streak (Int)      |           | test_results (JSON)   |           | points (Int)         |
| skills (JSON)     |           | created_at            |           | files (JSON)         |
| badges (JSON)     |           +-----------+-----------+           | test_cases (JSON)    |
| last_active_date  |                       |                       | bug_signature        |
+---------+---------+                       |1                      +----------+-----------+
          |                                 |                                  |
          |1                                v1                                 |1
          |                     +-----------------------+                      |
          +-------------------->|    ChallengeReport    |<---------------------+
          |                     +-----------------------+
          |                     | id (PK)               |
          |                     | user_id (FK)          |
          |                     | challenge_id (FK)     |
          |                     | submission_id (FK)    |
          |                     | report_type           |
          |                     | description           |
          v                     +-----------------------+
+-------------------+
|   Notification    |
+-------------------+
| id (PK)           |
| user_id (FK)      |
| title / message   |
| read (Bool)       |
+-------------------+
```

### Table Specs

#### 1. `buggyman_user` (`User` Model)
- **Primary Key**: `id` (Auto-Increment Integer)
- **Fields**: `username` (VARCHAR 150, Unique), `email` (VARCHAR 254, Unique), `password` (VARCHAR 128, Hashed), `role` (VARCHAR 20, default `'user'`), `total_score` (INT), `challenges_solved` (INT), `streak` (INT), `skills` (JSONB/JSON), `badges` (JSONB/JSON), `activities` (JSONB/JSON), `last_active_date` (DATE).

#### 2. `buggyman_challenge` (`Challenge` Model)
- **Primary Key**: `id` (Auto-Increment Integer / String ID)
- **Fields**: `title` (VARCHAR 255), `description` (TEXT), `status` (VARCHAR 20, default `'published'`), `difficulty` (VARCHAR 50), `technology` (VARCHAR 100), `category` (VARCHAR 100), `points` (INT), `files` (JSON), `test_cases` (JSON), `bug_signature` (TEXT), `suspected_component` (VARCHAR 255).
- **Index**: Index on `status`, `technology`, `difficulty`.

#### 3. `buggyman_submission` (`Submission` Model)
- **Primary Key**: `id` (Auto-Increment Integer)
- **Foreign Keys**: `user_id` $\rightarrow$ `User.id` (ON DELETE CASCADE), `challenge_id` $\rightarrow$ `Challenge.id` (ON DELETE CASCADE).
- **Fields**: `submitted_code` (TEXT), `submitted_files` (JSON), `success` (BOOLEAN), `score` (INT), `test_results` (JSON), `execution_time` (FLOAT), `attempt_number` (INT), `created_at` (DATETIME).

---

## 9. API Documentation & HTTP Lifecycle

| Method | Endpoint | Purpose | Request Body | Response Payload | Status Codes | Source Code |
|---|---|---|---|---|---|---|
| `POST` | `/api/register` | Register new user account | `{ fullName, username, email, password }` | `{ token, user: {...} }` | 200, 400 | `views.py:66-105` |
| `POST` | `/api/login` | Authenticate user credentials | `{ email, password }` | `{ token, user: {...} }` | 200, 401 | `views.py:41-62` |
| `GET` | `/api/challenges` | List published challenges | Query: `difficulty`, `search`, `arena` | `[ { id, title, points, ... } ]` | 200 | `views.py:193-258` |
| `GET` | `/api/challenges/:id` | Get challenge details | URL Param: `id` | `{ id, title, files, testCases }` | 200, 404 | `views.py:756-766` |
| `POST` | `/api/challenges/:id/run` | Run code without submission | `{ code, files }` | `{ success, testCases, stdout, stderr }` | 200, 429 | `views.py:790-823` |
| `POST` | `/api/challenges/:id/submit` | Submit code solution | `{ code, files }` | `{ success, score, aiSummary, ... }` | 200, 401, 429 | `views.py:894-970` |
| `GET` | `/api/challenges/recommendations` | Get ML challenge picks | Header: `Authorization` | `[ { challenge, recommendationScore } ]` | 200 | `views.py:590-620` |
| `POST` | `/api/challenges/generate` | AI Challenge Generator | `{ difficulty, technology, category }` | `{ id, title, files, testCases }` | 201 | `views.py:1428-1481` |
| `GET` | `/api/leaderboard` | Get global rankings | None | `[ { rank, username, totalScore } ]` | 200 | `views.py:1260-1285` |
| `GET` | `/api/admin/stats` | Admin platform metrics | Header: `Authorization` (Admin) | `{ totalUsers, totalChallenges, users }` | 200, 403 | `views.py:1310-1334` |

---

## 10. Authentication, Authorization & Security

### Security Features Implemented Matrix

| Security Feature | Implementation Status | Implementation Details | File & Code Reference |
|---|---|---|---|
| **Password Hashing** | **Implemented** | PBKDF2 with SHA-256 via Django `check_password()` & `make_password()` | `backend/buggyman/views.py:58` |
| **Password Strength Validation** | **Implemented** | Enforces length & common password checks via `validate_password()` | `backend/buggyman/views.py:97` |
| **JWT Token Authentication** | **Implemented** | Stateless HMAC-SHA256 tokens signed with `SECRET_KEY` (7-day expiry) | `backend/buggyman/auth.py:15-35` |
| **Role-Based Access Control (RBAC)** | **Implemented** | Admin endpoints protected by `is_admin_user(user)` checks | `backend/buggyman/views.py:1310` |
| **Sliding Window Rate Limiting** | **Implemented** | Django Cache sliding window limits ($10\text{ auth/min}$, $30\text{ exec/min}$) | `backend/buggyman/throttling.py:15-60` |
| **Sensitive Data Scrubbing** | **Implemented** | Recursively redacts `password`, `token`, `secret`, `jwt` before logging | `backend/buggyman/logger.py:12-26` |
| **SQL Injection Prevention** | **Implemented** | Django ORM parameterized queries; raw SQL adapter uses `?` bindings | `backend/buggyman/evaluator/runtimes.py:210` |
| **Execution Timeouts** | **Implemented** | Subprocess execution capped at $5.0\text{s}$ limit to prevent Denial of Service | `backend/buggyman/evaluator/sandboxes.py:35` |
| **CORS Isolation** | **Planned / Production** | Configured via Django CORS Headers middleware for production domain | `backend/settings.py` |

---

## 11. Algorithms & Computational Complexity

### Algorithm 1: Dynamic Runtime Adapter Resolution
- **Purpose**: Selects appropriate execution environment (`Python`, `Node`, `SQL`, `Static`) for incoming submissions.
- **Where Used**: `backend/buggyman/evaluator/engine.py` (`resolve_adapter` L29–L58).
- **Time Complexity**: $\mathcal{O}(1)$ lookup across technology string matches and file extension set intersection.
- **Space Complexity**: $\mathcal{O}(E)$ where $E$ is count of distinct file extensions.

### Algorithm 2: Sigmoidal Success Probability Calculation
- **Purpose**: Predicts user solve probability based on skill vector delta.
- **Formula**: $P(success) = \frac{1}{1 + e^{-2.2 \cdot \left(\frac{\text{Skill} - \text{Diff}}{35}\right)}}$
- **Where Used**: `backend/buggyman/ml/difficulty_predictor.py` (`predict_difficulty` L53–L58).
- **Time Complexity**: $\mathcal{O}(1)$ basic arithmetic evaluation.
- **Space Complexity**: $\mathcal{O}(1)$.

### Algorithm 3: Leaderboard Multi-Criteria Tie-Breaking
- **Purpose**: Orders developers on leaderboard deterministically without ambiguous ties.
- **Criteria Order**:
  1. Primary: `total_score` (Descending)
  2. Secondary: `challenges_solved` (Descending)
  3. Tertiary: Total attempts count (Ascending - penalizes excessive trial-and-error)
  4. Quaternary: `created_at` (Ascending - grants preference to earlier platform members)
- **Where Used**: `backend/buggyman/views.py` (`leaderboard_view` L1260–L1285).
- **Time Complexity**: $\mathcal{O}(U \log U)$ where $U$ is total user count.

---

## 12. Error Handling & Resiliency

### Error Taxonomy & Behavior

| Failure Scenario | Error Detection Mechanism | User/API Response | Recovery Action |
|---|---|---|---|
| **Syntax Error in Code** | Subprocess exit code $\neq 0$ or `stderr` capture | HTTP 200 with `success: false` and `stderr` displayed in Output Panel | User views error traceback and edits code in Monaco Editor |
| **Infinite Loop in Code** | `SubprocessSandboxRunner` process timeout ($5.0\text{s}$) | `timed_out: true`, "Execution timed out (5s limit exceeded)" | Subprocess is forcibly terminated via `process.kill()` |
| **Invalid Credentials** | Django `check_password()` returns `False` | HTTP 401 Unauthorized (`{"error": "Invalid credentials"}`) | User re-enters credentials |
| **Rate Limit Exceeded** | `apply_rate_limit()` cache count $> 30$ | HTTP 429 Too Many Requests (`{"error": "Rate limit exceeded"}`) | Client blocks further execution requests for $60\text{s}$ window |
| **Database Connection Failure** | Django ORM `OperationalError` exception | HTTP 500 Internal Server Error | Logged via `log_error_event()` for server investigation |

---

## 13. Performance & Scalability Blueprint

### Current Optimizations Implemented
1. **Cache Layer for Recommendations & Leaderboards**: Recommendation lists and leaderboard datasets are cached in Django `cache` for 30 seconds (`views.py:1272` & `recommender.py:17`), drastically reducing DB read load.
2. **Session Storage Workspace Caching**: IDE workspace state is saved in browser `sessionStorage` (`EditorPage.jsx:112`), eliminating redundant API round-trips while switching tabs.
3. **Lazy Subprocess Sandbox Spawning**: Execution environments are spawned only when execution is explicitly triggered by user action.

### Scaling Roadmap: 100 $\rightarrow$ 10,000 $\rightarrow$ 1,000,000 Users

```
   100 Users                 10,000 Users                        1,000,000 Users
+--------------+        +-------------------+           +---------------------------------+
| Single Node  |        | Django Cluster    |           | Microservices Architecture     |
| Django App   | -----> | PostgreSQL Master | --------> | Kubernetes Execution Pods       |
| SQLite DB    |        | Redis Cache Node  |           | Celery Distributed Queue        |
+--------------+        | Nginx Load Balancer|          | PostgreSQL Read Replicas        |
                        +-------------------+           | Cloudflare CDN + Edge Workers   |
                                                        +---------------------------------+
```

- **At 10,000 Users**: Migrate SQLite to PostgreSQL with connection pooling (PgBouncer); deploy Nginx load balancer across 3 Django backend instances; utilize Redis as shared cache and rate limiter.
- **At 1,000,000 Users**: Decouple execution engine into isolated Docker worker containers managed by Celery and RabbitMQ queues; split platform into Microservices (Auth Service, Catalog Service, Execution Sandbox Cluster, Analytics ML Worker Node).

---

## 14. Testing Suite & Quality Assurance

BuggyMan includes an extensive, automated test suite located in `backend/buggyman/tests.py` comprising **78 unit and integration tests**.

### Command to Execute Test Suite
```bash
cd backend
python manage.py test
```

### Test Coverage Highlights
- **Authentication Tests**: Registration, duplicate email rejection, password validation, login token issuing.
- **Catalog & Selection Tests**: Exact catalog size assertion (10 published challenges), difficulty breakdown assertions (3 Easy, 4 Medium, 3 Hard), search query keyword matching, technology filtering.
- **Evaluation Engine Tests**: Execution of correct vs buggy solutions across Python, JavaScript, and SQL.
- **Gamification Tests**: XP point accumulation, active streak incrementation, achievement badge unlocks.
- **Observability Tests**: Sensitive key redaction in logging module.

---

## 15. Important Architectural & Design Decisions

### Decision 1: Custom Subprocess Runner vs. Docker Container per Run
- **Chosen**: Subprocess Runner with $5.0\text{s}$ timeout limit (`sandboxes.py`).
- **Alternative**: Spawning an ephemeral Docker container for every execution request.
- **Why Preferred**: Subprocess startup takes $<10\text{ms}$ compared to $500\text{ms}-1.5\text{s}$ Docker container spin-up time. For an interactive learning platform, sub-second code feedback is critical for user experience.
- **Trade-off**: Requires careful environment isolation and path sanitization on the host operating system compared to absolute container isolation.

### Decision 2: REST API with Stateless JWT vs. Server-Side Django Sessions
- **Chosen**: Stateless JWT Authentication (`auth.py`).
- **Alternative**: Standard Django HTTP Session Cookies.
- **Why Preferred**: Enables complete decoupling of the React Vite frontend bundle from the Django backend server, simplifying deployment to separate static CDNs.
- **Trade-off**: Tokens cannot be instantly revoked server-side without maintaining a Redis token blacklist.

---

## 16. Real Engineering Challenges & Solutions

### Challenge 1: React State Immutability in Buggy Challenges
- **Problem**: When evaluating React code challenges, naive string matching failed when users solved bugs using alternative syntax (e.g. `setCount(prev => prev + 1)` vs `setCount(count + 1)`).
- **Diagnosis**: AST parsing was necessary to check logic intent rather than rigid regex literal string equality.
- **Solution**: Updated `NodeRuntimeAdapter` to execute user component files inside a Node test harness using regex pattern sets combined with structural output assertions.

### Challenge 2: SQL Sandbox Multi-File Schema Dependency
- **Problem**: Executing user `query.sql` files failed because SQLite in-memory databases lacked the underlying table definitions.
- **Diagnosis**: `query.sql` relied on `schema.sql` definitions which were stored separately in the challenge metadata.
- **Solution**: Enhanced `EvaluationEngine.evaluate()` (`engine.py:96-101`) to automatically detect SQL challenges, locate secondary setup files (`schema.sql`), and prepend execution sequence before executing user queries.

---

## 17. System Limitations & Honest Trade-Offs

1. **Subprocess Isolation Bounds**: While subprocesses run under time limits, malicious system calls (e.g. attempting to read host root directories) are restricted via Python environment scoping rather than full kernel-level namespace virtualization.
2. **Synchronous Execution Pipeline**: Code execution occurs synchronously within the HTTP request thread. Under extreme concurrency, worker threads could become saturated.

---

## 18. Production Readiness & Scalability Roadmap

- **Containerization**: Package Django app and React bundle into multi-stage Dockerfiles.
- **Asynchronous Task Queue**: Transition code execution to Celery workers backed by Redis.
- **Database Indexing**: Add composite indexes on `Submission(user_id, success)` and `Challenge(status, difficulty)`.

---

## 19. Deployment & Environment Setup Guide

### Local Development Setup

#### 1. Clone Repository & Setup Backend
```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed Database with Catalog Challenges
python manage.py seed_db

# Run Unit Tests to Verify Setup
python manage.py test

# Start Django Development Server
python manage.py runserver
```

#### 2. Setup Frontend
```bash
# Navigate to frontend folder in separate terminal
cd frontend

# Install Dependencies
npm install

# Start Vite Development Server
npm run dev
```

---

## 20. Complete File-by-File Codebase Directory

```
BuggyMan-main/
├── backend/
│   ├── backend/                # Django Project Config (settings.py, urls.py, wsgi.py)
│   ├── buggyman/               # Main Application App
│   │   ├── evaluator/          # Isolated Execution Engine
│   │   │   ├── engine.py       # Central EvaluationEngine class
│   │   │   ├── runtimes.py     # Language Adapters (Python, Node, SQL, Static)
│   │   │   └── sandboxes.py    # SubprocessSandboxRunner with timeouts
│   │   ├── ml/                 # Machine Learning & Adaptive Profiling
│   │   │   ├── skill_profiler.py      # SkillProfiler vector calculator
│   │   │   ├── difficulty_predictor.py# Sigmoidal DifficultyPredictor
│   │   │   ├── recommender.py         # ChallengeRecommender engine
│   │   │   └── analytics_collector.py # User dataset aggregator
│   │   ├── management/commands/
│   │   │   └── seed_db.py      # Database Seeder (10 catalog + special arenas)
│   │   ├── models.py           # Django Models (User, Challenge, Submission, etc.)
│   │   ├── views.py            # API View Controllers & Endpoints
│   │   ├── auth.py             # JWT Token authentication helpers
│   │   ├── throttling.py       # Sliding-window rate limiters
│   │   ├── logger.py           # Observability & sensitive data scrubber
│   │   └── tests.py            # 78 Automated Unit & Integration Tests
│   └── manage.py               # Django Management CLI
├── frontend/
│   ├── src/
│   │   ├── components/         # Shared UI (Navbar, Sidebar, Toast, FilterPanel)
│   │   ├── pages/              # Views (Dashboard, Analytics, Leaderboard, Admin)
│   │   │   ├── ChallengeSelection.jsx  # Code Challenges Catalog
│   │   │   ├── SQLChallenges.jsx       # SQL Lab Arena Catalog
│   │   │   ├── FrontendDesignChallenges.jsx # Frontend Studio Catalog
│   │   │   └── Challenge/              # Workspace IDE
│   │   │       ├── EditorPage.jsx          # IDE Main Container
│   │   │       ├── CodeEditor.jsx          # Monaco Editor Wrapper
│   │   │       ├── ProblemStatementPanel.jsx # Instructions & Tests
│   │   │       └── OutputPanel.jsx         # Console Execution Results
│   │   ├── services/           # Axios API Wrappers (authService, challengeService)
│   │   ├── App.jsx             # React App Root & Routes
│   │   └── index.css           # Global Tailwind & Semantic Theme Variables
│   └── vite.config.js          # Vite Build Configuration
└── README.md                   # This Preparation & Documentation Master Guide
```

---

## 21. Comprehensive Interview Question Bank

### Beginner Level
1. What is the core problem BuggyMan solves compared to LeetCode?
2. What technologies are used on the frontend vs. backend?
3. How are user passwords stored securely in the database?

### Intermediate Level
4. How does BuggyMan execute multi-language code safely?
5. Explain the purpose of `EvaluationEngine` in `engine.py`.
6. How does the rate limiter work in `throttling.py`?

### Advanced Level
7. Explain the mathematical formula used in `DifficultyPredictor`.
8. How does the SQL Lab execute queries against `schema.sql`?
9. How would you scale the execution engine to handle 100,000 concurrent submissions?

---

## 22. Model Answers for Technical Interviews

### Q: "How does BuggyMan ensure that execution timeouts don't hang the backend server?"
> **Model Answer**: "We enforce process timeouts inside `SubprocessSandboxRunner` located in `backend/buggyman/evaluator/sandboxes.py`. When a runtime adapter executes user code, `run_command()` spawns a process using Python's `subprocess.Popen`. We invoke `process.communicate(timeout=5.0)`. If execution exceeds 5 seconds, Python raises a `subprocess.TimeoutExpired` exception. Our exception handler immediately calls `process.kill()` to terminate the rogue subprocess and returns a structured dictionary with `timed_out: True`. This guarantees server worker threads are freed immediately."
> 
> **Code Reference**: `backend/buggyman/evaluator/sandboxes.py` $\rightarrow$ `SubprocessSandboxRunner.run_command()` $\rightarrow$ Lines 35–55.

---

## 23. Live Demo Script & Walkthrough Guide

1. **Open Dashboard**: "Notice the daily active streak counter and the ML-recommended challenges panel."
2. **Open Debugging Challenge**: Navigate to Code Challenges $\rightarrow$ Select `2. Search Bugs`.
3. **Show IDE**: "Here we have Monaco Editor loaded with multi-file starter code."
4. **Execute Run**: Click **Run Code** $\rightarrow$ show failure message in Output Panel.
5. **Fix Code**: Replace `bug.title.includes(query)` with `(bug.title || '').toLowerCase().includes(query.toLowerCase())`.
6. **Submit**: Click **Submit Solution** $\rightarrow$ show transition to `ResultPage` with XP awarded!

---

## 24. "Show Me the Code" Quick-Reference Map

| Topic | File to Open | Class / Function | Line Numbers |
|---|---|---|---|
| **Code Execution Engine** | `backend/buggyman/evaluator/engine.py` | `EvaluationEngine.evaluate()` | L59–L180 |
| **Subprocess Timeout Sandbox** | `backend/buggyman/evaluator/sandboxes.py` | `SubprocessSandboxRunner.run_command()` | L20–L65 |
| **ML Sigmoid Difficulty Predictor** | `backend/buggyman/ml/difficulty_predictor.py` | `DifficultyPredictor.predict_difficulty()` | L17–L95 |
| **Submission & XP Processing** | `backend/buggyman/views.py` | `submit_challenge_view()` | L894–L970 |
| **Rate Limiting Engine** | `backend/buggyman/throttling.py` | `apply_rate_limit()` | L15–L60 |
| **Monaco Editor Component** | `frontend/src/pages/Challenge/CodeEditor.jsx` | `CodeEditor()` | L5–L50 |

---

## 25. Final Interview Cheat Sheet

- **One-Sentence Summary**: BuggyMan is a full-stack debugging platform that evaluates developers on real-world code fixes using a sandboxed multi-language execution engine and an adaptive ML skill recommender.
- **Tech Stack**: React 18, Vite, Tailwind CSS, Monaco Editor, Django 5.0, DRF, SQLite/PostgreSQL, Python Subprocess Engine.
- **Top 3 Files**:
  1. `backend/buggyman/evaluator/engine.py` (Execution Sandbox Orchestration)
  2. `backend/buggyman/views.py` (API Controllers & Gamification Pipeline)
  3. `backend/buggyman/ml/difficulty_predictor.py` (ML Sigmoidal Profiler)
- **Core Algorithm**: Sigmoidal Success Probability Prediction ($P = \frac{1}{1 + e^{-2.2 \cdot \delta}}$).
- **Key Metrics**: 78 Automated Unit Tests Passing ($100\%$), 10 Published Core Catalog Challenges, 4 Runtime Environments Supported.
