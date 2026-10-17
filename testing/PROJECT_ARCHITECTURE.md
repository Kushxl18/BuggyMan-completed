# BuggyMan System Architecture Documentation

**Document ID:** ARCH-2026-v1.0  
**Project:** BuggyMan Interactive Debugging & Learning Platform  
**Target Environment:** Local Staging / Cloud Production  
**Last Audited:** October 16, 2026  

---

## 1. Executive Architecture Summary

BuggyMan is a dual-tier full-stack developer training and assessment ecosystem designed to simulate real-world debugging workflows across Algorithms, Databases (SQL), and Frontend Web Design (HTML/CSS/JS). The application features real-time code evaluation sandboxes, automated skill profiling and career path intelligence, a gamified economy (XP, Badges, Streaks, BugBytes virtual currency), competitive multiplayer (PvP battles), and OAuth 2.0 Single Sign-On (Google & GitHub).

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                CLIENT TIER (SPA)                                 │
│  React 18 + Vite 5 + Tailwind CSS v3.4 + Lucide Icons + Monaco Editor            │
│  State: Context / React Hooks + LocalStorage Session Security                    │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ HTTPS / REST JSON / JWT Bearer
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                               BACKEND API SERVICE                                │
│  Django 5.1 + Django REST Framework + SimpleJWT Token Authentication             │
│  - Endpoint Routing & Throttling (Rate Limiting)                                 │
│  - Secure Sandboxed Code Evaluation Engine (Subprocess / AST / SQLite In-Memory) │
│  - Career Recommendation Engine & Adaptive Difficulty Controller                 │
│  - PvP Battle Session & Matchmaking Controller                                   │
│  - BugBytes Virtual Economy & Simulative Refund Reconciliation                   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ PostgreSQL Connection (SSL)
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                DATA STORAGE TIER                                 │
│  PostgreSQL (Neon Cloud / Local Engine) with Zero-Config SQLite Fallback         │
│  Relational Models: Users, Challenges, Submissions, Battles, Economy, Reports   │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Architecture (Client Tier)

### 2.1 Technology Stack
- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.4.21
- **Styling:** Tailwind CSS 3.4.19 with custom design tokens, dark/light theme support
- **Code Editor:** `@monaco-editor/react` 4.7.0 (Microsoft Monaco Editor integration)
- **Routing:** `react-router-dom` 6.22.3
- **Icons:** `lucide-react`
- **Charts:** `recharts` 2.12.3

### 2.2 Component Hierarchy & Layouts
1. **Public/Unauthenticated Shell:**
   - `/login`: Form validation, Google & GitHub SSO OAuth buttons.
   - `/register`: Multi-step user onboarding and profile initialization.
   - `/forgot-password`: Password reset request flow.
   - `/auth/callback`: OAuth 2.0 authorization code exchange and PKCE receiver.
2. **Authenticated Application Shell (`AuthenticatedLayout`):**
   - **Navbar:** Profile avatar, active BugBytes balance, XP indicator, notification center modal, dark/light mode toggle.
   - **Sidebar:** Navigation links (Dashboard, Catalog, SQL, Frontend, PvP, Leaderboard, Career Insights, Store, Settings, Admin).
3. **Dedicated Fullscreen Workspaces (Isolated from Navigation Shell):**
   - `/challenge/:id` (`EditorPage.jsx`): Split-pane Monaco editor, problem description, test runner, output terminal, AI hints.
   - `/pvp/arena/:battleId` (`PvPArena.jsx`): Dual-player synchronized arena, real-time countdown timer, test pass progress bars, rematch triggers.

---

## 3. Backend Architecture (Service Tier)

### 3.1 Technology Stack
- **Framework:** Django 5.1.4
- **API Framework:** Django REST Framework (DRF) 3.15.2
- **Authentication:** Custom JWT Bearer Authentication (`buggyman.auth.JWTAuthentication`) using SHA-256 HMAC tokens with 7-day expiration and sliding refresh tokens.
- **Security Throttling:** IP-based and User-based rate limiting (`buggyman.throttling.apply_rate_limit`).
- **Database Driver:** `psycopg2-binary` (PostgreSQL) / `django.db.backends.sqlite3` fallback.

### 3.2 Evaluation Engines & Sandboxing (`buggyman.evaluator`)
- **Python Code Evaluation:**
  - Sandboxed execution via subprocess isolation with enforced execution timeout (default: 5.0 seconds).
  - Memory and system call restriction logic.
  - Test case assertion runner evaluating public and hidden assertions against structured stdout/stderr.
- **SQL Execution Sandbox:**
  - Executes schema definitions and user SQL queries in an isolated in-memory SQLite database instance per test case.
  - Automatically isolates tables and prevents cross-tenant data leakage.
- **Frontend Studio Evaluation:**
  - Executes HTML/CSS/JavaScript within a secured browser iframe context (`sandbox="allow-scripts"`).

---

## 4. Machine Learning & Career Recommendation Layer (`buggyman.ml`)

- **Skill Profiler (`skill_profiler.py`):** Calculates multi-dimensional developer mastery across categories (State, Algorithmic, Concurrency, SQL, Frontend) based on historical solve rate, penalty time, and hint reliance.
- **Recommender Engine (`recommender.py`):** Dynamic challenge selection matching identified user weaknesses and onboarding preferences (`strengths`, `weaknesses`, `interests`).
- **Career Insights Engine (`career_engine.py`):** Analyzes target developer job roles (Full Stack Engineer, Backend Specialist, Frontend Developer, Data Engineer, QA Automation Engineer), scores user readiness percentage, and creates actionable targeted learning paths.

---

## 5. Gamification, Economy & PvP Architecture

- **Streak Engine:** Timezone-aware localdate calculation with lapse detection.
- **XP & Levels:** Linear scaling with level thresholds and achievement badges.
- **BugBytes Store & Refund Reconciliation:**
  - Virtual currency purchases with INR simulation.
  - Timed Challenge Refund: If a user unlocks a paid challenge and solves it within the challenge time limit, **their real currency (INR) is refunded**, while BugBytes balance remains unaffected.
- **PvP Battle Engine:** Matchmaking queue, room creation with custom codes, test passing progress polling, countdown timers, and automatic forfeit/expiry resolution.

---

## 6. External Integrations & Out-of-Scope Services

- **OAuth 2.0 Providers:**
  - Google Identity (OAuth 2.0 Authorization Code flow)
  - GitHub OAuth (Developer App code exchange)
  - *Note:* LinkedIn OAuth was fully purged in Phase 2.
- **AI Services (Groq / Gemini / OpenAI):**
  - Groq Llama 3 for intelligent contextual hint generation and solution explanation.
  - Fallback deterministic heuristic hints when AI API credentials are not provided.
- **Out of Scope / Future Implementations:**
  - Real Razorpay / Stripe payment gateway (simulated mode currently active per project requirements).
  - ChromaDB / Vector RAG document embedding store (currently out of scope; project uses relational challenge data).
