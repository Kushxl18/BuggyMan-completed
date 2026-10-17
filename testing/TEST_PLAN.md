# BuggyMan Master Test Plan

**Document ID:** PLAN-2026-v1.0  
**Project:** BuggyMan Interactive Learning Platform  
**Target Release:** v1.0.0 (Production Candidate)  
**Lead QA Architect:** Senior Quality Engineer  
**Date:** October 16, 2026  

---

## 1. Scope & Objective

The objective of this comprehensive quality assurance engagement is to validate BuggyMan end-to-end against functional specifications, performance baselines, security standards, and production readiness requirements.

### In-Scope
- **Authentication & User Management:** Registration, login, JWT token issuance, session refresh, profile management, Google/GitHub SSO.
- **Challenge Execution Engines:** Multi-file code evaluation for Python, SQL, and Frontend Design (HTML/CSS/JS).
- **Gamification Mechanics:** Daily streaks (timezone-aware lapse detection), XP rewards, level thresholds, and global leaderboard calculation.
- **Career Intelligence Engine:** Profile parsing, skill gap analysis, and tailored recommendations targeting user weaknesses.
- **Virtual Economy & Refund Reconciliations:** BugBytes packages, wallet ledger, and timed challenge solve refund reconciliation (guaranteeing real money is refunded upon on-time challenge completion).
- **PvP Multiplayer Arena:** Matchmaking queue, room creation, status polling, countdown timer expiration, and solution submission race conditions.
- **Security & Integrity:** Rate limiting, input validation, SQL injection barriers, and cross-user data isolation.
- **Production Build:** Vite production compilation and Django system checks.

### Out-of-Scope (Explicitly Documented)
- **Live Payment Gateway (Razorpay/Stripe):** Simulated checkout flow active per instruction (`dont do real payment integration yet`).
- **LinkedIn OAuth 2.0:** Removed completely from the application codebase.
- **ChromaDB / Vector RAG Stores:** Contextual AI hints use direct Groq Llama completion rather than vector retrieval databases.

---

## 2. Test Execution Schedule & Phasing

| Phase | Focus Area | Tools / Harness | Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Repository & Architecture Audit | Static Inspection, Route Mapping | Architecture & Inventory Markdown Files |
| **Phase 2** | Test Design & Traceability | Specification Mapping | Test Cases & Traceability Matrix |
| **Phase 3** | Backend & Sandbox Test Execution| Django Test Runner, Coverage.py | Unit & Integration Test Reports |
| **Phase 4** | API Contract & Security Testing | DRF APIClient, Boundary Scripts | API & Security Test Reports |
| **Phase 5** | Frontend Production Build & UI | Vite Build Engine, Component Verification | Build Logs & Smoke Test Reports |
| **Phase 6** | Performance & Concurrency | Subprocess stress tests | Latency & Performance Reports |
| **Phase 7** | Defect Management & Re-testing | Code Inspection & Regression Harness | Bug Reports & Retest Evidence |
| **Phase 8** | Final Quality Audit & Sign-off | Comprehensive Review | Final Summary & Go/No-Go Recommendation|

---

## 3. Entry & Exit Criteria

### Entry Criteria
1. Backend system check passes with `0 issues` (`python manage.py check`).
2. Database migrations are fully applied to Neon PostgreSQL (`python manage.py migrate`).
3. Frontend dependencies installed and bundle compiles cleanly (`npm run build`).

### Exit Criteria
1. 100% of planned test cases executed with documented Pass/Fail status.
2. 0 Critical (P0) or High (P1) defects remaining unresolved.
3. Code coverage reports generated and stored under `testing/evidence/`.
4. All workbooks (`REQUIREMENT_TRACEABILITY_MATRIX.xlsx`, `TEST_CASES.xlsx`, `TEST_EXECUTION_RESULTS.xlsx`, `BUG_REPORTS.xlsx`) generated and verified.
5. All 17 mandatory documentation files complete and cross-linked.
