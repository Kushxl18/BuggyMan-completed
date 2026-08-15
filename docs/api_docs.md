# BuggyMan REST API Reference

All API requests are routed under `/api/` and expect/return `application/json`.
Authenticated requests require the header: `Authorization: Bearer <jwt_token>`.

---

## 1. Authentication Endpoints

### `POST /api/login`
Authenticates a user and returns a JWT token.
- **Request Body**:
  ```json
  { "email": "student@college.edu", "password": "password123" }
  ```
- **Response `200 OK`**:
  ```json
  { "token": "<jwt>", "user": { "id": 1, "username": "student", "role": "user", "totalScore": 100 } }
  ```

### `POST /api/register`
Registers a new student user.
- **Response `201 Created`**:
  ```json
  { "token": "<jwt>", "user": { "id": 2, "username": "new_student", "role": "user" } }
  ```

### `GET /api/profile`
Fetches the current user's profile, XP, streak, and unlocked badges.

---

## 2. Challenge & Execution Endpoints

### `GET /api/challenges`
Returns published debugging challenges filtered by query params (`difficulty`, `technology`, `category`, `search`).

### `GET /api/challenges/<id>`
Fetches detailed problem statement, starter code files, and test case requirements for a challenge.

### `POST /api/challenges/<id>/run`
Executes code in an isolated subprocess sandbox without recording official submission results.
- **Request Body**:
  ```json
  { "code": "function fix() {}", "files": [{ "name": "App.jsx", "content": "..." }] }
  ```
- **Response `200 OK`**:
  ```json
  { "success": true, "stdout": "...", "stderr": "", "testCases": [...] }
  ```

### `POST /api/challenges/<id>/submit`
Submits code for official evaluation, calculates score, updates user streak, and records submission.

---

## 3. AI Intelligence Suite Endpoints

### `POST /api/challenges/<id>/hint`
Generates progressive AI hints (Level 1, 2, or 3).

### `POST /api/challenges/<id>/feedback`
Generates diagnostic AI feedback analyzing test failures.

### `POST /api/challenges/<id>/explain`
Generates step-by-step post-submission solution explanation.

### `POST /api/challenges/generate`
Generates a new valid debugging challenge with automated evaluation validation.

---

## 4. Machine Learning & Analytics Endpoints

### `GET /api/challenges/recommendations`
Returns ML personalized challenge recommendations.

### `GET /api/challenges/learning-path`
Returns a 5-stage personalized learning curriculum.

### `GET /api/analytics`
Returns accuracy rate, attempt metrics, and difficulty progression.

### `GET /api/analytics/weaknesses`
Returns detected category failure rates and error patterns.

---

## 5. Gamification & Leaderboard Endpoints

### `GET /api/leaderboard`
Returns top 50 ranked students calculated via multi-column ordering and dense rank logic.

---

## 6. Observability & Admin Endpoints

### `GET /api/health`
Health check endpoint reporting database, evaluator, and cache status (`200 OK` or `503`).

### `GET /api/admin/backup/export` (Admin Only)
Exports full JSON database backup snapshot.

### `POST /api/admin/backup/verify` (Admin Only)
Validates integrity and count checksums of a backup JSON payload.
