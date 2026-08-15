# BuggyMan — AI-Powered Software Debugging & Learning Platform

BuggyMan is an interactive, gamified software debugging laboratory and adaptive learning platform. Designed for computer science students and software engineers, BuggyMan shifts coding education from writing code from scratch to **diagnosing, isolating, and repairing real software bugs** across full-stack applications, database queries, and user interfaces.

---

## 🌟 Key Features

- **3 Specialized Debugging Arenas**:
  - **Code Lab**: Debug JavaScript, React state mutations, Node.js async logic, and Python algorithmic errors.
  - **SQL Lab**: Fix broken SQL queries, missing `WHERE` clauses, incorrect `ORDER BY` directions, schema constraints, and `JOIN` logic in an in-memory SQLite sandbox.
  - **Frontend Studio**: Repair broken CSS layouts, Flexbox/Grid alignment bugs, responsive breakpoints, and accessibility defects.
- **AI Intelligence Suite**:
  - **Graduated Hints**: Level 1 (Conceptual Direction), Level 2 (Targeted Guidance), Level 3 (Solution Clues).
  - **AI Diagnostic Feedback**: Analyzes test failures and pinpoints root-cause code defects.
  - **Solution Explainer**: Step-by-step post-submission breakdown of bug root causes.
  - **AI Challenge Generator**: Generates new valid debugging challenges on demand with automated test verification.
  - **Synthetic Bug Injector**: Inject logic, state mutation, or API bugs into clean code.
- **Adaptive Machine Learning Engine**:
  - **Analytics Collector**: Classifies errors (`syntax_error`, `state_mutation_error`, `database_error`, `runtime_error`).
  - **Difficulty Predictor**: Multi-factor difficulty estimation (1.0 to 3.0 scale).
  - **Personalized Recommender**: Hybrid collaborative & content-based challenge recommendations.
  - **Adaptive Difficulty Trajectory**: Dynamically adjusts challenge difficulty based on performance.
  - **Weakness Detector**: Identifies recurring failure patterns and category weaknesses.
  - **Learning Path Generator**: Constructs 5-stage personalized learning curricula.
- **Production-Ready & Secure**:
  - **Sandbox Isolation**: Subprocess isolation with ephemeral temp directories, path traversal stripping, and host environment scrubbing.
  - **Sliding-Window Rate Limiting**: Protects auth, code execution, and AI endpoints against abuse (`HTTP 429`).
  - **Role-Based Access Control (RBAC)**: Admin vs Student user roles guarding management endpoints.
  - **Observability & Logging**: Health check monitoring (`/api/health`) and sensitive log sanitization.
  - **Backup & Integrity Check**: Full platform JSON database export and integrity verification.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+
- **npm**: 9+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py test  # Verify all 76 unit tests pass
python manage.py runserver 0.0.0.0:8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🛠 Tech Stack

- **Frontend**: React 18, Vite, TailwindCSS, CodeMirror 6, Lucide Icons, Recharts.
- **Backend**: Django 4.2+, Django REST Framework, SQLite (In-Memory Sandbox), PyJWT.
- **Testing**: Django Test Suite (76 unit tests), Vite Build Verification.
- **Evaluation Engine**: Subprocess execution isolation with Node.js Jest and Python unittest harnesses.

---

## 📚 Documentation Links

- [Architecture & System Design](docs/architecture.md)
- [REST API Reference](docs/api_docs.md)
- [Environment Setup Guide](docs/setup_guide.md)
