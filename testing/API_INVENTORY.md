# BuggyMan API Inventory & Endpoint Catalog

**Document ID:** API-INV-2026-v1.0  
**Base URL:** `/api/`  
**Authentication:** Header `Authorization: Bearer <jwt_token>`  
**Last Audited:** October 16, 2026  

---

## 1. Authentication & User Profile Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/login` | POST | None (AllowAny) | 10/min | User login with email/password; returns JWT and user payload |
| `/api/register` | POST | None (AllowAny) | 5/min | User registration; creates account and returns JWT |
| `/api/check-availability` | GET | None (AllowAny) | 30/min | Validates email or username availability during registration |
| `/api/profile` | GET, PUT | Yes (IsAuthenticated)| 60/min | Retrieve or update user profile, avatar, preferences |
| `/api/profile/skill-matrix` | GET | Yes (IsAuthenticated)| 30/min | Returns multi-axis skill competency breakdown |
| `/api/logout` | POST | Yes (IsAuthenticated)| 20/min | Invalidates user session |

---

## 2. OAuth 2.0 / SSO Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/auth/oauth/config` | GET | None (AllowAny) | 60/min | Returns configured OAuth providers (Google, GitHub) |
| `/api/auth/oauth/callback` | POST | None (AllowAny) | 20/min | Code exchange for OAuth token and user provisioning |
| `/api/auth/oauth` | POST | None (AllowAny) | 15/min | Direct SSO registration/login |
| `/api/auth/oauth/disconnect`| POST | Yes (IsAuthenticated)| 10/min | Disconnects third-party OAuth provider from account |

---

## 3. Challenge & Evaluation Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/challenges` | GET | None (AllowAny) | 60/min | Catalog listing with filters (tech, category, difficulty) |
| `/api/challenges/<pk>` | GET | None (AllowAny) | 60/min | Challenge details, code files, and public test cases |
| `/api/challenges/<pk>/run` | POST | Yes (IsAuthenticated)| 30/min | Sandbox execution of user code against sample tests |
| `/api/challenges/<pk>/submit`| POST | Yes (IsAuthenticated)| 20/min | Official submission; evaluates against all tests and awards XP |
| `/api/challenges/<pk>/hint` | POST | Yes (IsAuthenticated)| 15/min | Generates AI hint via Groq Llama; costs BugBytes |
| `/api/challenges/<pk>/hints`| GET | Yes (IsAuthenticated)| 30/min | Retrieves previously unlocked hints for challenge |
| `/api/challenges/<pk>/feedback`| POST| Yes (IsAuthenticated)| 15/min | Automated code quality feedback and tips |
| `/api/challenges/<pk>/explain` | POST| Yes (IsAuthenticated)| 15/min | In-depth AI explanation of solution architecture |
| `/api/challenges/<pk>/submissions`| GET| Yes (IsAuthenticated)| 30/min | Historical submissions for a challenge |
| `/api/submissions` | GET | Yes (IsAuthenticated)| 30/min | User submission history log |
| `/api/submissions/<pk>` | GET | Yes (IsAuthenticated)| 30/min | Submission detail view with execution logs |
| `/api/challenges/<pk>/report`| POST | Yes (IsAuthenticated)| 10/min | Submit bug report or issue with challenge |

---

## 4. Analytics & Career Insights Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/analytics` | GET | Yes (IsAuthenticated)| 30/min | Aggregated user solving statistics and trends |
| `/api/analytics/ai-insights` | GET | Yes (IsAuthenticated)| 15/min | Automated AI summary of learning trajectory |
| `/api/analytics/weaknesses` | GET | Yes (IsAuthenticated)| 30/min | List of detected user weakness tags |
| `/api/career-insights` | GET | Yes (IsAuthenticated)| 30/min | Role readiness scores and targeted recommendations |
| `/api/leaderboard` | GET | None (AllowAny) | 60/min | Global leaderboard ranked by XP and streaks |

---

## 5. Virtual Economy & BugBytes Store Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/bugbytes` | GET | Yes (IsAuthenticated)| 60/min | User BugBytes balance and transaction summary |
| `/api/bugbytes/history` | GET | Yes (IsAuthenticated)| 30/min | BugBytes transaction history |
| `/api/store/packages` | GET | None (AllowAny) | 60/min | Catalog of BugBytes credit packages |
| `/api/store/checkout` | POST | Yes (IsAuthenticated)| 15/min | Initiates order and simulation session |
| `/api/store/confirm-payment`| POST | Yes (IsAuthenticated)| 15/min | Confirms payment and credits BugBytes to balance |
| `/api/store/purchases` | GET | Yes (IsAuthenticated)| 30/min | Historical purchases and refund statuses |
| `/api/store/purchases/<pk>/refund`| POST| Yes (IsAuthenticated)| 10/min | Timed challenge solve refund reconciliation |

---

## 6. PvP Battles Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/pvp/create` | POST | Yes (IsAuthenticated)| 30/min | Creates new PvP battle room with custom room code |
| `/api/pvp/join` | POST | Yes (IsAuthenticated)| 30/min | Joins battle room by room code |
| `/api/pvp/quick-match` | POST | Yes (IsAuthenticated)| 30/min | Instant matchmaking with queued player |
| `/api/pvp/history` | GET | Yes (IsAuthenticated)| 30/min | Historical PvP match records |
| `/api/pvp/<pk>/status` | GET | Yes (IsAuthenticated)| 60/min | Live battle status and opponent progress polling |
| `/api/pvp/<pk>/start` | POST | Yes (IsAuthenticated)| 30/min | Transitions battle to IN_PROGRESS |
| `/api/pvp/<pk>/progress` | POST | Yes (IsAuthenticated)| 60/min | Updates player's live test case passing count |
| `/api/pvp/<pk>/submit` | POST | Yes (IsAuthenticated)| 20/min | Submits solution to determine winner |
| `/api/pvp/<pk>/cancel` | POST | Yes (IsAuthenticated)| 30/min | Cancels pending room |

---

## 7. Administrative & Health Endpoints

| Endpoint | Method | Auth Required | Rate Limit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/admin/stats` | GET | Admin / Staff | 30/min | Platform-wide operational analytics |
| `/api/admin/users` | GET | Admin / Staff | 30/min | User accounts management |
| `/api/admin/challenges/create`| POST | Admin / Staff | 20/min | Custom challenge creator |
| `/api/admin/reports` | GET | Admin / Staff | 30/min | Challenge problem reports |
| `/api/admin/backup/export` | GET | Admin / Staff | 5/min | Database backup snapshot exporter |
| `/api/admin/backup/verify` | POST | Admin / Staff | 5/min | Integrity verification of database snapshots |
| `/api/health` | GET | None (AllowAny) | None | System uptime and database health check |
