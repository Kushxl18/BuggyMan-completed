# BuggyMan QA & Test Strategy

**Document ID:** STRAT-2026-v1.0  
**Project:** BuggyMan Interactive Platform  
**Target Quality Level:** Production Readiness (Zero Critical Defects)  
**Author:** Senior QA Architect & Test Engineer  
**Date:** October 16, 2026  

---

## 1. Testing Philosophy & Guiding Principles

1. **Zero Fabrication:** Never manufacture test results, pass rates, code coverage figures, or defects. Every documented result must stem from reproducible command execution or verified log evidence.
2. **Safe & Non-Destructive Execution:** Test databases and sandboxed environments must always be isolated from live user data. Never reset or overwrite production credentials or databases.
3. **Traceability Matrix:** Every functional requirement traces through test case IDs, automated execution scripts, genuine log evidence, and tracked defect items.
4. **Honest Boundary Demarcation:** Distinctly separate verified locally-tested features from mocked/simulated services (e.g. simulated Razorpay payments vs live banking APIs, deterministic AI fallback vs live Groq API keys).

---

## 2. Test Levels & Methodology

```
┌────────────────────────────────────────────────────────┐
│                   TEST PYRAMID                         │
├────────────────────────────────────────────────────────┤
│           End-to-End & Smoke Tests (5%)                │
│       • Full user lifecycle (Signup -> Solve -> XP)    │
│       • PvP Matchmaking & live session completion      │
├────────────────────────────────────────────────────────┤
│        Integration & API Contract Tests (35%)          │
│       • REST API response schemas & HTTP status codes  │
│       • Authentication, token expiry & role isolation  │
│       • Code runner sandbox isolation & timeout guards │
├────────────────────────────────────────────────────────┤
│             Unit & Model Tests (60%)                   │
│       • Database model constraints & custom methods    │
│       • Streak calculation across day/tz boundaries    │
│       • Recommender engine & career readiness formulas │
│       • BugBytes refund calculations & wallet ledger   │
└────────────────────────────────────────────────────────┘
```

### 2.1 Unit Testing (Backend & Frontend)
- **Backend:** Python `unittest` / Django `TestCase` testing model methods, serializer validators, rate limiters, evaluation adapters (Python, SQL, Frontend), and skill profiling algorithms.
- **Frontend:** Component sanity verification and Vite production build validation (`npm run build`).

### 2.2 API & Integration Testing
- Comprehensive DRF `APIClient` requests hitting all 45+ registered endpoints across valid inputs, boundary values, malformed payloads, unauthenticated states, and cross-user data tampering.

### 2.3 Sandboxed Security & Isolation Testing
- **Subprocess Isolation:** Verifying infinite loops (`while True: pass`) hit the 5.0-second execution cutoff without exhausting server CPU.
- **SQL Security:** Verifying destructive injection and extension loading (`ATTACH DATABASE`, `load_extension`) are intercepted and safely aborted.
- **Cross-User Data Isolation:** Verifying User A cannot access or modify User B's submissions, purchases, or profile records.

### 2.4 Performance & Reliability Testing
- Measuring API response latency under rapid sequential requests.
- Validating database connection pool stability and memory retention during sustained evaluation runs.

---

## 3. Test Environment Specifications

- **OS:** Windows 11 Enterprise (PowerShell 7 / pwsh)
- **Backend:** Python 3.13.2, Django 5.1.4, Django REST Framework 3.15.2
- **Database:** PostgreSQL (Neon Cloud / Local SSL instance) with SQLite In-Memory for SQL challenge sandbox execution
- **Frontend:** Node.js v20.18.0, Vite 5.4.21, React 18.2.0
- **Test Automation Tools:** `unittest`, `pytest-django`, `coverage.py`, `openpyxl` (workbook generation)

---

## 4. Defect Severity & Classification Standard

- **Critical (P0):** Application crash, data corruption, security bypass, or inability to register/login/execute code.
- **High (P1):** Major functional flaw without obvious workaround (e.g., incorrect XP/streak deduction, broken evaluation scoring).
- **Medium (P2):** Secondary feature defect with partial workaround (e.g., UI layout misalignment in specific viewports, non-blocking warning).
- **Low (P3):** Cosmetic inconsistency, spelling typo, or minor enhancement suggestion.
