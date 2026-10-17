# BuggyMan Feature Inventory & Functional Matrix

**Document ID:** FEAT-INV-2026-v1.0  
**Project:** BuggyMan  
**Version:** 1.0.0 (Production Candidate)  
**Last Audited:** October 16, 2026  

---

## 1. Feature Inventory Summary Table

| Feature ID | Module / Domain | Feature Name | Description | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FEAT-AUTH-01** | Authentication | Email/Password Registration | User account registration with validation and profile setup | Verified Active |
| **FEAT-AUTH-02** | Authentication | Email/Password Login | Secure authentication with JWT token issuance | Verified Active |
| **FEAT-AUTH-03** | Authentication | Google OAuth 2.0 SSO | 1-click Google Cloud Identity authentication | Verified Active |
| **FEAT-AUTH-04** | Authentication | GitHub OAuth 2.0 SSO | 1-click GitHub Developer identity authentication | Verified Active |
| **FEAT-AUTH-05** | Authentication | Password Recovery Flow | Simulative password reset link generation | Verified Active |
| **FEAT-AUTH-06** | Authentication | Token Refresh & Logout | Session termination and token invalidation | Verified Active |
| **FEAT-AUTH-07** | Authentication | New User Onboarding | Post-signup track, experience & skill preference setup | Verified Active |
| **FEAT-CHAL-01** | Challenge Engine | Core Challenge Catalog | Multi-filter challenge browser (Tech, Difficulty, Category) | Verified Active |
| **FEAT-CHAL-02** | Challenge Engine | Challenge Detail View | Comprehensive problem statement, constraints & metadata | Verified Active |
| **FEAT-CHAL-03** | Challenge Engine | Code Runner (Test Mode) | Non-scoring test execution against sample test cases | Verified Active |
| **FEAT-CHAL-04** | Challenge Engine | Solution Submission | Final code submission with evaluation against hidden tests | Verified Active |
| **FEAT-CHAL-05** | Challenge Engine | AI Contextual Hint System| Dynamic hints powered by Groq Llama with cost deduction | Verified Active |
| **FEAT-CHAL-06** | Challenge Engine | SQL Interactive Studio | In-browser SQL schema runner with test verification | Verified Active |
| **FEAT-CHAL-07** | Challenge Engine | Frontend Design Studio | HTML/CSS/JS preview in isolated browser iframe | Verified Active |
| **FEAT-GAME-01** | Gamification | XP & Level Progression | Score-to-level progression algorithm | Verified Active |
| **FEAT-GAME-02** | Gamification | Daily Streak Engine | Timezone-aware localdate calculation with lapse check | Verified Active |
| **FEAT-GAME-03** | Gamification | Global Leaderboard | Ranking by XP, Streaks, and Challenges Solved | Verified Active |
| **FEAT-GAME-04** | Gamification | User Skill Matrix | 5-axis developer radar profiling (State, SQL, etc.) | Verified Active |
| **FEAT-PVP-01** | PvP Multiplayer | Quick Matchmaking | Automated pairing with active queued developers | Verified Active |
| **FEAT-PVP-02** | PvP Multiplayer | Custom Room Creation | 6-character room codes with difficulty & timer settings | Verified Active |
| **FEAT-PVP-03** | PvP Multiplayer | Room Code Join | Joining friend's battle room via room code | Verified Active |
| **FEAT-PVP-04** | PvP Multiplayer | Live Battle Arena | Synchronized editor, opponent test progress & countdown | Verified Active |
| **FEAT-PVP-05** | PvP Multiplayer | Auto-Completion & Expiry | Expiration triggers when timer hits zero | Verified Active |
| **FEAT-ECON-01** | Virtual Economy | BugBytes Balance Tracking| In-app currency accounting and transaction ledger | Verified Active |
| **FEAT-ECON-02** | Virtual Economy | Package Purchase Sim | Currency top-ups via simulated Razorpay payment flow | Verified Active |
| **FEAT-ECON-03** | Virtual Economy | Timed Challenge Refund | User's real money refunded upon challenge completion in time | Verified Active |
| **FEAT-CARE-01** | Career Insights | Role Readiness Scoring | Percentage readiness calculations for industry roles | Verified Active |
| **FEAT-CARE-02** | Career Insights | Weakness-Targeted Paths | Recommendations prioritized by user weak areas | Verified Active |
| **FEAT-ADMN-01** | Administration | System Statistics | High-level metrics on users, submissions, and pass rates | Verified Active |
| **FEAT-ADMN-02** | Administration | Challenge Authoring | Admin portal to create/edit custom coding challenges | Verified Active |
| **FEAT-ADMN-03** | Administration | Report Management | User problem report resolution and moderation | Verified Active |

---

## 2. Out-of-Scope / Deferred Features

The following features were evaluated and identified as non-implemented, intentionally simulated, or deferred:

1. **Real Payment Gateway Integration:**
   - **Status:** Deferred per explicit instruction (`dont do real payment integration yet`).
   - **Current Implementation:** Simulated checkout and webhook confirmation.
2. **LinkedIn OAuth 2.0:**
   - **Status:** Completely Removed per user instruction (`remove login through linkedin completely`).
3. **ChromaDB / Vector RAG Embeddings:**
   - **Status:** Out of Scope. AI hints use direct contextual prompting via Groq/OpenAI rather than vector retrieval databases.
