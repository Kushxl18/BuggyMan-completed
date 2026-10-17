# BuggyMan Test Environment Specification

**Document ID:** ENV-SPEC-2026-v1.0  
**Project:** BuggyMan  
**Version:** 1.0.0  
**Last Verified:** October 16, 2026  

---

## 1. Host System Environment

- **Operating System:** Windows 11 Enterprise (64-bit)
- **Shell:** PowerShell 7.5.0 (`pwsh`)
- **Working Directory:** `c:\Users\Kushal\OneDrive\Desktop\BuggyMan-main` (Symlinked to `D:\BuggyMan-main`)

---

## 2. Backend Environment

- **Python Runtime:** Python 3.13.2
- **Framework:** Django 5.1.4
- **REST Framework:** Django REST Framework 3.15.2
- **Token Security:** SimpleJWT 5.3.1 (HMAC-SHA256 signature, 7-day expiration)
- **Database Driver:** `psycopg2-binary` (PostgreSQL engine)
- **Primary Database:** PostgreSQL 16 on Neon Cloud (`ep-rapid-wind-...neon.tech/neondb` with SSL)
- **Secondary / Sandbox Database:** SQLite in-memory engine for dynamic SQL challenge evaluation (`sqlite3`)
- **Sandbox Evaluation:** Python `subprocess` with 5.0-second timeout enforcement

---

## 3. Frontend Environment

- **Node.js Runtime:** v20.18.0
- **Package Manager:** npm v10.8.2
- **Build Engine:** Vite 5.4.21
- **UI Framework:** React 18.2.0
- **Styling Engine:** Tailwind CSS 3.4.19
- **Monaco Editor:** `@monaco-editor/react` 4.7.0
- **Routing:** `react-router-dom` 6.22.3

---

## 4. Test Harnesses & Automation Libraries

- **Unit/Integration Testing:** Django Test Framework (`django.test.TestCase`), `rest_framework.test.APIClient`
- **Coverage Tooling:** `coverage` 7.16.2
- **Report Generation:** `openpyxl` 3.1.5 (Microsoft Excel format generation)
- **Static Syntax Check:** Django System Check Framework (`manage.py check`)

---

## 5. Required Environment Variable Specifications (Sanitized)

*Per security policy, live secrets are omitted; only variable names and purposes are documented.*

| Variable Name | Required | Purpose |
| :--- | :--- | :--- |
| `SECRET_KEY` | Yes | Django cryptographic signing key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `FRONTEND_BASE_URL` | Yes | Base URL for CORS and OAuth callbacks |
| `GROQ_API_KEY` | Optional | Groq AI cloud API key for contextual hints |
| `GOOGLE_CLIENT_ID` | Optional | Google OAuth 2.0 Web Client ID |
| `GOOGLE_CLIENT_SECRET` | Optional | Google OAuth 2.0 Client Secret |
| `GITHUB_CLIENT_ID` | Optional | GitHub Developer OAuth App Client ID |
| `GITHUB_CLIENT_SECRET` | Optional | GitHub Developer OAuth App Client Secret |
| `RAZORPAY_KEY_ID` | Optional | Payment gateway key (simulated mode active) |
| `RAZORPAY_KEY_SECRET` | Optional | Payment gateway secret (simulated mode active) |
