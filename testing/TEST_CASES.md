# BuggyMan Comprehensive Test Cases Specification

**Document ID:** TC-SPEC-2026-v1.0  
**Project:** BuggyMan  
**Version:** 1.0.0  
**Last Updated:** October 16, 2026  

---

## Section A: Authentication & User Management (TC-AUTH)

### TC-AUTH-001: Valid User Registration
- **Feature:** User Account Registration (`FEAT-AUTH-01`)
- **Objective:** Verify a new user can successfully register with valid details.
- **Preconditions:** Email and username must not exist in database.
- **Test Data:** `username: "testrunner1"`, `email: "runner1@example.com"`, `password: "SecurePass123!"`
- **Steps:**
  1. Send `POST /api/register` with test data payload.
  2. Inspect response status code and payload.
- **Expected Result:** HTTP 200 OK or 201 Created; returns JWT token and user profile dictionary.
- **Severity/Priority:** Critical / P0

### TC-AUTH-002: Duplicate Email Registration Rejection
- **Feature:** Registration Validation (`FEAT-AUTH-01`)
- **Objective:** Verify system prevents registering an existing email address.
- **Preconditions:** An account with `test@example.com` exists.
- **Steps:**
  1. Send `POST /api/register` with `email: "test@example.com"`.
- **Expected Result:** HTTP 400 Bad Request; error message indicates email is already in use.
- **Severity/Priority:** High / P1

### TC-AUTH-003: Valid User Login
- **Feature:** User Authentication (`FEAT-AUTH-02`)
- **Objective:** Verify authenticated user receives a valid JWT token.
- **Steps:**
  1. Send `POST /api/login` with registered credentials.
- **Expected Result:** HTTP 200 OK; returns JWT token string, user details, and active streak.
- **Severity/Priority:** Critical / P0

### TC-AUTH-004: Invalid Password Rejection
- **Feature:** Authentication Security (`FEAT-AUTH-02`)
- **Objective:** Verify login fails when providing incorrect password.
- **Steps:**
  1. Send `POST /api/login` with wrong password.
- **Expected Result:** HTTP 401 Unauthorized; returns invalid credentials error without leaking specifics.
- **Severity/Priority:** High / P1

### TC-AUTH-005: Protected Endpoint Rejection for Unauthenticated Requests
- **Feature:** Token Authorization (`FEAT-AUTH-02`)
- **Objective:** Verify endpoints requiring authentication reject requests missing Bearer tokens.
- **Steps:**
  1. Send `GET /api/profile` without Authorization header.
- **Expected Result:** HTTP 401 Unauthorized or 403 Forbidden.
- **Severity/Priority:** Critical / P0

### TC-AUTH-006: Google OAuth 2.0 Redirection URL Generation
- **Feature:** Google SSO (`FEAT-AUTH-03`)
- **Objective:** Verify public OAuth config returns authentic Google client ID and authorization URL.
- **Steps:**
  1. Send `GET /api/auth/oauth/config`.
- **Expected Result:** HTTP 200 OK; providers object contains Google metadata and valid auth URL.
- **Severity/Priority:** High / P1

### TC-AUTH-007: GitHub OAuth 2.0 Redirection URL Generation
- **Feature:** GitHub SSO (`FEAT-AUTH-04`)
- **Objective:** Verify public OAuth config returns authentic GitHub client ID and authorization URL.
- **Steps:**
  1. Send `GET /api/auth/oauth/config`.
- **Expected Result:** HTTP 200 OK; providers object contains GitHub metadata and valid auth URL.
- **Severity/Priority:** High / P1

### TC-AUTH-008: Verify LinkedIn Provider Is Absent
- **Feature:** OAuth Provider Whitelist (`FEAT-AUTH-03`, `FEAT-AUTH-04`)
- **Objective:** Verify LinkedIn is completely absent from available OAuth providers.
- **Steps:**
  1. Send `GET /api/auth/oauth/config`.
  2. Send `POST /api/auth/oauth` with `provider: "linkedin"`.
- **Expected Result:** `config.providers.linkedin` is undefined; POST returns HTTP 400 Unsupported Provider.
- **Severity/Priority:** High / P1

---

## Section B: Coding Challenge Evaluation & Sandboxing (TC-EVAL)

### TC-EVAL-001: Correct Python Solution Run
- **Feature:** Sandbox Execution (`FEAT-CHAL-03`)
- **Objective:** Verify valid Python code passes sample test assertions in sandbox.
- **Steps:**
  1. Send `POST /api/challenges/<pk>/run` with correct solution function.
- **Expected Result:** HTTP 200 OK; `success: true`, all test cases marked passed.
- **Severity/Priority:** Critical / P0

### TC-EVAL-002: Incorrect Python Solution Run
- **Feature:** Sandbox Execution (`FEAT-CHAL-03`)
- **Objective:** Verify buggy code reports failed test assertions and detailed stdout/stderr diff.
- **Steps:**
  1. Send `POST /api/challenges/<pk>/run` with failing logic.
- **Expected Result:** HTTP 200 OK; `success: false`, failing test case captures mismatch.
- **Severity/Priority:** High / P1

### TC-EVAL-003: Subprocess Infinite Loop Timeout Guard
- **Feature:** Code Isolation & Security (`FEAT-CHAL-03`)
- **Objective:** Verify infinite loops (`while True: pass`) are killed at 5.0 seconds.
- **Steps:**
  1. Send `POST /api/challenges/<pk>/run` with `while True: pass`.
- **Expected Result:** HTTP 200 OK; `success: false`, stderr reports execution timeout error.
- **Severity/Priority:** Critical / P0

### TC-EVAL-004: Interactive SQL Challenge Evaluation
- **Feature:** SQL Sandbox Engine (`FEAT-CHAL-06`)
- **Objective:** Verify correct SQL query returns matching rows against in-memory SQLite schema.
- **Steps:**
  1. Send `POST /api/challenges/SQL-E01/run` with `SELECT * FROM orders WHERE status = 'completed';`.
- **Expected Result:** HTTP 200 OK; `success: true`, result set contains filtered rows.
- **Severity/Priority:** Critical / P0

### TC-EVAL-005: Destructive SQL Query Blocking
- **Feature:** SQL Sandbox Security (`FEAT-CHAL-06`)
- **Objective:** Verify SQL runner blocks `ATTACH DATABASE` and extension loading attempts.
- **Steps:**
  1. Evaluate query `SELECT load_extension("exploit.so");`.
- **Expected Result:** Execution halted; `SECURITY_ERROR` returned.
- **Severity/Priority:** Critical / P0

### TC-EVAL-006: Solution Submission & XP Award
- **Feature:** Challenge Submission (`FEAT-CHAL-04`)
- **Objective:** Verify successful solution submission awards XP, increments solved count, and logs record.
- **Steps:**
  1. Send `POST /api/challenges/<pk>/submit` with passing solution.
- **Expected Result:** HTTP 200 OK; user total score increases by challenge points, submission saved.
- **Severity/Priority:** Critical / P0

---

## Section C: Gamification, Streaks & Career Insights (TC-GAME & TC-CARE)

### TC-GAME-001: Streak Increment on Consecutive Day
- **Feature:** Daily Streaks (`FEAT-GAME-02`)
- **Objective:** Verify user streak increments by 1 when solving a challenge on consecutive days.
- **Steps:**
  1. Record submission yesterday (`current_streak: 1`).
  2. Record submission today.
- **Expected Result:** `current_streak` becomes 2.
- **Severity/Priority:** High / P1

### TC-GAME-002: Streak Lapse Detection
- **Feature:** Daily Streaks (`FEAT-GAME-02`)
- **Objective:** Verify user streak resets to 1 if more than 1 calendar day has elapsed since last solve.
- **Steps:**
  1. Set last solve date to 3 days ago with streak 10.
  2. Solve a challenge today.
- **Expected Result:** Streak resets to 1; lapse detected.
- **Severity/Priority:** High / P1

### TC-GAME-003: Global Leaderboard Ranking Order
- **Feature:** Leaderboard (`FEAT-GAME-03`)
- **Objective:** Verify users are sorted in descending order of XP and total score.
- **Steps:**
  1. Fetch `GET /api/leaderboard`.
- **Expected Result:** Leaderboard entries ordered strictly with highest XP first.
- **Severity/Priority:** High / P1

### TC-CARE-001: Career Insights Role Readiness Calculation
- **Feature:** Career Engine (`FEAT-CARE-01`)
- **Objective:** Verify readiness percentage reflects solved challenges matching role skills.
- **Steps:**
  1. Fetch `GET /api/career-insights` for user.
- **Expected Result:** Returns role scores (e.g., Full Stack Engineer, Backend Specialist) between 0% and 100%.
- **Severity/Priority:** High / P1

### TC-CARE-002: Personalized Recommendations Match User Weaknesses
- **Feature:** Career Engine Recommendations (`FEAT-CARE-02`)
- **Objective:** Verify recommendations prioritize challenge categories listed in user profile weaknesses.
- **Steps:**
  1. Set user weaknesses to `['SQL', 'Concurrency']`.
  2. Request `GET /api/challenges/recommendations`.
- **Expected Result:** Recommended challenges prominently feature SQL and Concurrency topics.
- **Severity/Priority:** High / P1

---

## Section D: Virtual Economy & Timed Challenge Refund (TC-ECON)

### TC-ECON-001: BugBytes Package Purchase Simulation
- **Feature:** Store Simulation (`FEAT-ECON-02`)
- **Objective:** Verify purchasing a BugBytes package credits tokens to balance.
- **Steps:**
  1. Send `POST /api/store/checkout` for 100 BugBytes package.
  2. Confirm payment simulation via `POST /api/store/confirm-payment`.
- **Expected Result:** User `bugbytes_balance` increases by 100; ledger transaction logged.
- **Severity/Priority:** High / P1

### TC-ECON-002: Timed Challenge Solve Refund Reconciliation
- **Feature:** Money Refund Reconciliation (`FEAT-ECON-03`)
- **Objective:** Verify that solving an unlocked paid challenge within time refunds strictly user's money (INR) and NOT virtual BugBytes.
- **Steps:**
  1. Unlock challenge with purchase record.
  2. Submit passing solution within allotted time limit.
  3. Inspect refund transaction record.
- **Expected Result:** Real currency refund status marked COMPLETED with refund amount in INR; BugBytes balance remains unchanged.
- **Severity/Priority:** Critical / P0

---

## Section E: PvP Multiplayer Arena (TC-PVP)

### TC-PVP-001: PvP Room Creation
- **Feature:** PvP Room (`FEAT-PVP-02`)
- **Objective:** Verify creator receives unique 6-character room code and battle room enters WAITING status.
- **Steps:**
  1. Send `POST /api/pvp/create` with difficulty filter and time limit.
- **Expected Result:** Battle record created with unique room code, status `WAITING`.
- **Severity/Priority:** High / P1

### TC-PVP-002: PvP Room Code Join
- **Feature:** PvP Matchmaking (`FEAT-PVP-03`)
- **Objective:** Verify player 2 can join room code; status transitions to `MATCHED`.
- **Steps:**
  1. Player 2 sends `POST /api/pvp/join` with room code.
- **Expected Result:** HTTP 200 OK; status changes to `MATCHED`, both players assigned.
- **Severity/Priority:** High / P1

### TC-PVP-003: Battle Progress Synchronization
- **Feature:** Live Arena (`FEAT-PVP-04`)
- **Objective:** Verify test passing updates reflect on opponent's polling stream.
- **Steps:**
  1. Send `POST /api/pvp/<pk>/progress` with `testsPassed: 3, testsTotal: 5`.
  2. Query `GET /api/pvp/<pk>/status`.
- **Expected Result:** `player1Progress.testsPassed` equals 3.
- **Severity/Priority:** High / P1

---

## Section F: Security, Rate Limiting & Infrastructure (TC-SEC & TC-FE)

### TC-SEC-001: Rate Limiter Throttles Rapid Requests
- **Feature:** Throttling (`FEAT-SEC-01`)
- **Objective:** Verify exceeding endpoint request limits triggers HTTP 429 Too Many Requests.
- **Steps:**
  1. Send rapid bursts of requests exceeding the rate limit window.
- **Expected Result:** HTTP 429 Too Many Requests with retry header.
- **Severity/Priority:** High / P1

### TC-FE-001: Production Bundle Compilation
- **Feature:** Frontend Build (`FEAT-FE-01`)
- **Objective:** Verify Vite builds frontend application bundle with zero errors or unresolved imports.
- **Steps:**
  1. Execute `npm run build` in `frontend/`.
- **Expected Result:** Exit code 0; optimized assets generated in `frontend/dist/`.
- **Severity/Priority:** Critical / P0
