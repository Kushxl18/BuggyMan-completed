# BuggyMan System Architecture & Technical Design

This document details the actual production architecture, component interactions, sandbox isolation models, machine learning algorithms, and security infrastructure of BuggyMan.

---

## 1. System Overview

BuggyMan is structured as a decoupled client-server architecture with isolated evaluation environments and machine learning services:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER (React 18)                              │
│         Vite + TailwindCSS + CodeMirror 6 + Recharts + Lucide Icons + React Router     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ REST API (JSON / Bearer JWT)
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                                 BACKEND API GATEWAY (Django DRF)                       │
│  Rate Limiter (throttling.py) ── RBAC Security Guard ── Sensitive Key Redactor (logger.py)  │
└──────────────┬────────────────────────────┬────────────────────────────┬───────────────┘
               │                            │                            │
┌──────────────▼─────────────┐ ┌────────────▼──────────────┐ ┌───────────▼───────────────┐
│     EVALUATION ENGINE      │ │    ADAPTIVE ML ENGINE     │ │  AI INTELLIGENCE SUITE   │
│ Subprocess Execution       │ │ Analytics Collector      │ │ Hint Generator            │
│ Ephemeral Temp Directory   │ │ Difficulty Predictor     │ │ Diagnostic Feedback       │
│ Host Env Scrubbing         │ │ Challenge Recommender    │ │ Solution Explainer        │
│ Python -I -B Isolation     │ │ Weakness Detector        │ │ AI Challenge Generator    │
│ SQLite In-Memory Sandbox   │ │ Learning Path Generator  │ │ Synthetic Bug Injector    │
└────────────────────────────┘ └──────────────────────────┘ └───────────────────────────┘
```

---

## 2. Frontend Architecture

The frontend is built using **React 18** bundled with **Vite**:

- **Code Editor**: Integrated **CodeMirror 6** (`CodeEditor.jsx`) supporting JavaScript/JSX, Python, and SQL syntax highlighting, line numbers, light/dark themes, and workspace state persistence.
- **Routing & Navigation**: `react-router-dom` managing unauthenticated routes (`/login`, `/register`, `/forgot-password`), workspace route (`/challenge/:id`), and authenticated layout routes (`/dashboard`, `/challenges`, `/sql-challenges`, `/design-challenges`, `/leaderboard`, `/analytics`, `/profile`, `/admin`, `/notifications`, `/settings`).
- **Responsive Drawer & Layout**: Mobile drawer overlay (`isMobileMenuOpen`) toggled via hamburger navigation.
- **State & Service Layer**: Modular HTTP wrapper (`api.js`) and API services (`authService.js`, `challengeService.js`) handling token storage, error toasts, and rate-limit retry headers.

---

## 3. Backend Architecture

Built on **Django 4.2+** and **Django REST Framework (DRF)**:

- **Monolithic App Structure**: Main app package `buggyman/` containing models, DRF views, URL routers, authentication middleware, throttling engines, loggers, backup utilities, and ML submodules.
- **Service Layer**:
  - `buggyman/auth.py`: JWT token generation, validation, and user profile sync.
  - `buggyman/evaluator.py`: Multi-language subprocess sandbox evaluation engine.
  - `buggyman/throttling.py`: Sliding window rate limiter for auth, code execution, and AI requests.
  - `buggyman/logger.py`: Structured event logging and sensitive data redactor.
  - `buggyman/backup.py`: Full JSON backup exporter and integrity validator.

---

## 4. Database Schema & Data Models

Managed via Django ORM (`buggyman/models.py`):

```text
  ┌──────────────────┐            ┌──────────────────┐
  │       User       │ 1       N  │    Submission    │
  ├──────────────────┤───────────►├──────────────────┤
  │ id               │            │ id               │
  │ username         │            │ user_id          │
  │ email            │            │ challenge_id     │
  │ role (user/admin)│            │ code             │
  │ total_score      │            │ success          │
  │ streak           │            │ execution_time   │
  │ challenges_solved│            │ test_results     │
  └────────┬─────────┘            └─────────▲────────┘
           │ 1                              │ 1
           │                                │
           │ N                            N │
  ┌────────▼─────────┐            ┌─────────┴────────┐
  │ ChallengeReport  │            │    Challenge     │
  ├──────────────────┤            ├──────────────────┤
  │ id               │            │ id               │
  │ user_id          │            │ title            │
  │ challenge_id     │            │ difficulty       │
  │ report_type      │            │ technology       │
  │ status           │            │ status           │
  └──────────────────┘            └──────────────────┘
```

---

## 5. Evaluation Engine & Sandbox Isolation

Execution security is enforced by `SubprocessSandboxRunner` (`buggyman/evaluator.py`):

1. **Directory Isolation**: Every execution creates an isolated, ephemeral temporary directory (`tempfile.mkdtemp()`).
2. **Filesystem Traversal Prevention**: Strips all relative directory paths (`../../`) from user file names.
3. **Environment Scrubbing**: Clears all host environment variables except safe execution paths (`PATH`, `TEMP`, `SYSTEMROOT`).
4. **Python Security Flags**: Executes Python via `python -I -B` (isolated mode, ignore environment variables, do not write byte-code files).
5. **Timeout Limits**: Enforces hard process execution timeout limit (default: 10.0 seconds).
6. **Cleanup**: Recursively purges temporary directories (`shutil.rmtree`) in `finally` blocks.

---

## 6. SQL & Frontend Evaluation Arenas

- **SQL Arena Sandbox**: Executes SQL queries against an in-memory SQLite database (`:memory:`). Blocks command execution and dangerous extensions (`load_extension`).
- **Frontend Studio Arena**: Evaluates HTML, CSS, Flexbox/Grid layouts, and DOM assertions inside isolated sandboxes.

---

## 7. AI Intelligence Suite

Submodule `ai-engine/` and DRF endpoints:
- **Graduated Hints**: Generates Level 1 (Conceptual), Level 2 (Directional), and Level 3 (Solution Clues) hints without spoiling full solutions.
- **Diagnostic Feedback**: Analyzes test outputs (`stdout`, `stderr`) to diagnose root-cause defects.
- **Solution Explainer**: Generates post-submission code explanations.
- **AI Challenge Generator**: Generates complete, valid debugging challenges with automated test verification.
- **Synthetic Bug Injector**: Injects logic or state mutation bugs into clean code templates.

---

## 8. Machine Learning & Adaptive Learning Layer

Submodule `buggyman/ml/`:
- **Analytics Collector** (`analytics_collector.py`): Classifies errors into `syntax_error`, `runtime_error`, `database_error`, `state_mutation_error`, `timeout_error`, and `assertion_failure`.
- **Difficulty Predictor** (`difficulty_predictor.py`): Computes estimated difficulty ratings (1.0 to 3.0 scale).
- **Composite Recommender** (`recommender.py`): Recommends challenges matching user weakness areas and difficulty trajectory.
- **Adaptive Difficulty Engine** (`adaptive_difficulty.py`): Adjusts target difficulty based on consecutive successes or failures.
- **Weakness Detector** (`weakness_detector.py`): Detects category failure rates and recurring error patterns.
- **Learning Path Generator** (`learning_path.py`): Generates 5-stage personalized learning paths.

---

## 9. Security Audit & Access Control

- **Authentication**: Bearer JWT tokens signed with `HS256`. 401 response on invalid/expired tokens.
- **RBAC**: Enforces `is_admin_user(user)` returning `403 Forbidden` for non-admin users on `/api/admin/*`.
- **Rate Limiting**: Sliding window history limiting `auth` (10/min), `code_execution` (30/min), and `ai_request` (15/min). Returns `429 Too Many Requests`.
- **Sensitive Key Redaction**: `sanitize_data()` recursively masks `password`, `token`, `secret`, `api_key`, and `jwt` fields in logs.

---

## 10. Environment Variables

| Variable | Default Value | Purpose |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | Django cryptographic signing key |
| `DEBUG` | `True` | Enable/disable debug mode |
| `ALLOWED_HOSTS` | `*` | Allowed host headers |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins |
| `STATIC_ROOT` | `<BASE_DIR>/staticfiles` | Target directory for `collectstatic` |
