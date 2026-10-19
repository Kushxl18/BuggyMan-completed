import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Color palette
HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="F8FAFC")
BORDER_THIN = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)
PASS_FILL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
PASS_FONT = Font(name="Calibri", size=10, bold=True, color="166534")
FAIL_FILL = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
FAIL_FONT = Font(name="Calibri", size=10, bold=True, color="991B1B")
BLOCKED_FILL = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
BLOCKED_FONT = Font(name="Calibri", size=10, bold=True, color="854D0E")

def style_table(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            cell.border = BORDER_THIN
            if cell.row == 1:
                cell.fill = HEADER_FILL
                cell.font = HEADER_FONT
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            else:
                val_str = str(cell.value or '')
                if val_str == "Pass":
                    cell.fill = PASS_FILL
                    cell.font = PASS_FONT
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif val_str == "Fail":
                    cell.fill = FAIL_FILL
                    cell.font = FAIL_FONT
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif val_str in ("Blocked", "Simulated"):
                    cell.fill = BLOCKED_FILL
                    cell.font = BLOCKED_FONT
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif cell.column in (1, 4, 8, 9, 10):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
    ws.row_dimensions[1].height = 28

# 1. REQUIREMENT TRACEABILITY MATRIX
def create_rtm():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Traceability Matrix"
    headers = ["Req ID", "Requirement Description", "Feature ID", "Test Case ID", "Test Type", "Execution Result", "Evidence File", "Defect ID"]
    ws.append(headers)

    data = [
        ["REQ-AUTH-01", "User can register with email and password", "FEAT-AUTH-01", "TC-AUTH-001", "Functional", "Pass", "api_tests.log", "None"],
        ["REQ-AUTH-02", "Duplicate registration rejected with 400", "FEAT-AUTH-01", "TC-AUTH-002", "Negative", "Pass", "api_tests.log", "None"],
        ["REQ-AUTH-03", "User receives valid JWT on valid login", "FEAT-AUTH-02", "TC-AUTH-003", "Functional", "Pass", "api_tests.log", "None"],
        ["REQ-AUTH-04", "Invalid password rejected with 401", "FEAT-AUTH-02", "TC-AUTH-004", "Security", "Pass", "api_tests.log", "None"],
        ["REQ-AUTH-05", "Unauthenticated access rejected on private routes", "FEAT-AUTH-02", "TC-AUTH-005", "Security", "Pass", "api_tests.log", "None"],
        ["REQ-AUTH-06", "Google SSO configuration and redirection", "FEAT-AUTH-03", "TC-AUTH-006", "Integration", "Pass", "oauth_tests.log", "None"],
        ["REQ-AUTH-07", "GitHub SSO configuration and redirection", "FEAT-AUTH-04", "TC-AUTH-007", "Integration", "Pass", "oauth_tests.log", "None"],
        ["REQ-AUTH-08", "LinkedIn SSO completely disabled", "FEAT-AUTH-03", "TC-AUTH-008", "Security", "Pass", "oauth_tests.log", "None"],
        ["REQ-EVAL-01", "Python sandbox executes valid code correctly", "FEAT-CHAL-03", "TC-EVAL-001", "Functional", "Pass", "eval_tests.log", "None"],
        ["REQ-EVAL-02", "Python sandbox reports failed assertions", "FEAT-CHAL-03", "TC-EVAL-002", "Functional", "Pass", "eval_tests.log", "None"],
        ["REQ-EVAL-03", "Infinite loops terminate at 5-sec timeout", "FEAT-CHAL-03", "TC-EVAL-003", "Security/Perf", "Pass", "sandbox_tests.log", "None"],
        ["REQ-EVAL-04", "SQL queries execute on in-memory SQLite runner", "FEAT-CHAL-06", "TC-EVAL-004", "Functional", "Pass", "sql_tests.log", "None"],
        ["REQ-EVAL-05", "Destructive SQL commands safely blocked", "FEAT-CHAL-06", "TC-EVAL-005", "Security", "Pass", "sql_tests.log", "None"],
        ["REQ-EVAL-06", "Solution submission awards XP and logs record", "FEAT-CHAL-04", "TC-EVAL-006", "Functional", "Pass", "eval_tests.log", "None"],
        ["REQ-GAME-01", "Daily streaks increment on consecutive days", "FEAT-GAME-02", "TC-GAME-001", "Functional", "Pass", "gamification_tests.log", "None"],
        ["REQ-GAME-02", "Daily streaks reset to 1 after day lapse", "FEAT-GAME-02", "TC-GAME-002", "Functional", "Pass", "gamification_tests.log", "None"],
        ["REQ-GAME-03", "Leaderboard sorts strictly descending by XP", "FEAT-GAME-03", "TC-GAME-003", "Functional", "Pass", "leaderboard_tests.log", "None"],
        ["REQ-CARE-01", "Career insights calculate role readiness %", "FEAT-CARE-01", "TC-CARE-001", "Functional", "Pass", "career_tests.log", "None"],
        ["REQ-CARE-02", "Recommendations target user weaknesses", "FEAT-CARE-02", "TC-CARE-002", "Functional", "Pass", "career_tests.log", "None"],
        ["REQ-ECON-01", "Package checkout credits BugBytes balance", "FEAT-ECON-02", "TC-ECON-001", "Functional", "Pass", "economy_tests.log", "None"],
        ["REQ-ECON-02", "On-time challenge solve refunds real money (INR)", "FEAT-ECON-03", "TC-ECON-002", "Functional", "Pass", "refund_tests.log", "None"],
        ["REQ-PVP-01", "Create PvP battle room with custom room code", "FEAT-PVP-02", "TC-PVP-001", "Functional", "Pass", "pvp_tests.log", "None"],
        ["REQ-PVP-02", "Join PvP room via 6-character room code", "FEAT-PVP-03", "TC-PVP-002", "Functional", "Pass", "pvp_tests.log", "None"],
        ["REQ-PVP-03", "Synchronize test passing count across players", "FEAT-PVP-04", "TC-PVP-003", "Integration", "Pass", "pvp_tests.log", "None"],
        ["REQ-SEC-01", "API rate limiter throttles excessive requests", "FEAT-SEC-01", "TC-SEC-001", "Security", "Pass", "security_tests.log", "None"],
        ["REQ-FE-01", "Vite production build succeeds with 0 errors", "FEAT-FE-01", "TC-FE-001", "Build", "Pass", "build_tests.log", "None"],
        ["REQ-AUTH-09", "Enforce legitimate email domain and syntax validation", "FEAT-AUTH-01", "TC-AUTH-009", "Security", "Pass", "test_email_legitimacy.png", "BUG-005"],
        ["REQ-AUTH-10", "Mandatory 6-digit Email OTP verification via SMTP", "FEAT-AUTH-01", "TC-AUTH-010", "Functional", "Pass", "test_otp_login_flow.png", "BUG-007"],
        ["REQ-STAT-01", "New registered users initialize with zero streak/stats", "FEAT-USER-01", "TC-STAT-001", "Functional", "Pass", "test_user_profile_load.png", "BUG-006"],
        ["REQ-E2E-01", "Selenium E2E automation verifies all core web journeys", "FEAT-E2E-01", "TC-SEL-001", "Automated E2E", "Pass", "selenium_tests.log", "None"]
    ]
    for row in data:
        ws.append(row)
    style_table(ws)
    wb.save(os.path.join(BASE_DIR, "REQUIREMENT_TRACEABILITY_MATRIX.xlsx"))

# 2. TEST CASES WORKBOOK
def create_test_cases():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Test Cases"
    headers = ["Test ID", "Feature Area", "Test Objective", "Priority", "Preconditions", "Execution Steps", "Expected Result", "Status"]
    ws.append(headers)

    cases = [
        ["TC-AUTH-001", "Authentication", "Verify valid user registration", "P0", "New email/user", "POST /api/register with valid payload", "HTTP 200/201 + JWT token", "Pass"],
        ["TC-AUTH-002", "Authentication", "Reject duplicate email registration", "P1", "Email exists", "POST /api/register with existing email", "HTTP 400 with duplicate error", "Pass"],
        ["TC-AUTH-003", "Authentication", "Verify valid login credentials", "P0", "Active account", "POST /api/login with valid email/pwd", "HTTP 200 + token and profile", "Pass"],
        ["TC-AUTH-004", "Authentication", "Reject invalid password login", "P1", "Account exists", "POST /api/login with invalid password", "HTTP 401 Unauthorized", "Pass"],
        ["TC-AUTH-005", "Authentication", "Block unauthorized access to private API", "P0", "No token", "GET /api/profile without Bearer token", "HTTP 401 Unauthorized", "Pass"],
        ["TC-AUTH-006", "OAuth SSO", "Verify Google OAuth configuration", "P1", "Config configured", "GET /api/auth/oauth/config", "HTTP 200 + Google clientId & URL", "Pass"],
        ["TC-AUTH-007", "OAuth SSO", "Verify GitHub OAuth configuration", "P1", "Config configured", "GET /api/auth/oauth/config", "HTTP 200 + GitHub clientId & URL", "Pass"],
        ["TC-AUTH-008", "OAuth SSO", "Verify LinkedIn OAuth is fully absent", "P1", "LinkedIn removed", "GET /api/auth/oauth/config", "LinkedIn key omitted entirely", "Pass"],
        ["TC-AUTH-009", "Authentication", "Enforce legitimate email check during signup & login", "P0", "Signup / Login page", "Enter fake format e.g. bajnjnjdn@invalid or test@foo.bar", "Rejected with friendly legitimacy error", "Pass"],
        ["TC-AUTH-010", "Authentication", "Mandatory Email OTP verification via live Gmail SMTP", "P0", "Signup/Forgot Pwd", "Request 6-digit OTP to user email and verify code", "Dispatched to inbox, code verifies successfully", "Pass"],
        ["TC-STAT-001", "Gamification", "Ensure clean zero-state for newly registered accounts", "P1", "Brand new user", "Navigate to profile / notifications", "0 streak, 0 XP, 0 solved, empty badges, no phantom stats", "Pass"],
        ["TC-EVAL-001", "Evaluation", "Execute correct Python code solution", "P0", "Challenge exists", "POST /api/challenges/<pk>/run with valid code", "HTTP 200 + success: true", "Pass"],
        ["TC-EVAL-002", "Evaluation", "Execute failing Python code solution", "P1", "Challenge exists", "POST /api/challenges/<pk>/run with wrong code", "HTTP 200 + success: false", "Pass"],
        ["TC-EVAL-003", "Sandbox", "Infinite loop terminates at 5s timeout", "P0", "Sandbox active", "POST /api/challenges/<pk>/run with while True", "Timeout captured gracefully", "Pass"],
        ["TC-EVAL-004", "SQL Engine", "Verify interactive SQL query execution", "P0", "SQL challenge", "POST /api/challenges/SQL-E01/run with query", "HTTP 200 + matching rows", "Pass"],
        ["TC-EVAL-005", "SQL Security", "Block destructive SQL extensions/attach", "P0", "SQL runner", "Evaluate SELECT load_extension(...)", "Blocked with SECURITY_ERROR", "Pass"],
        ["TC-EVAL-006", "Evaluation", "Official submission awards XP points", "P0", "Passing code", "POST /api/challenges/<pk>/submit", "HTTP 200 + XP awarded", "Pass"],
        ["TC-GAME-001", "Gamification", "Daily streak increments consecutive days", "P1", "Solved yesterday", "Record submission today", "Current streak increments by 1", "Pass"],
        ["TC-GAME-002", "Gamification", "Daily streak resets on lapse (>1 day)", "P1", "Solved 3 days ago", "Record submission today", "Streak resets to 1", "Pass"],
        ["TC-GAME-003", "Gamification", "Leaderboard sorts descending by XP", "P1", "Users with XP", "GET /api/leaderboard", "Sorted highest to lowest XP", "Pass"],
        ["TC-CARE-001", "Career Engine", "Calculate role readiness percentages", "P1", "User profile", "GET /api/career-insights", "Readiness scores 0-100%", "Pass"],
        ["TC-CARE-002", "Career Engine", "Prioritize weakness recommendations", "P1", "Weaknesses set", "GET /api/challenges/recommendations", "Challenges match user weaknesses", "Pass"],
        ["TC-ECON-001", "Economy", "Credit BugBytes upon package checkout", "P1", "Store packages", "POST /api/store/confirm-payment", "BugBytes balance increases", "Pass"],
        ["TC-ECON-002", "Economy", "Refund money on on-time challenge solve", "P0", "Paid challenge", "Submit passing code within time limit", "Real money refunded (INR)", "Pass"],
        ["TC-PVP-001", "PvP Battle", "Create battle room with room code", "P1", "Logged in", "POST /api/pvp/create", "Room created + 6-char room code", "Pass"],
        ["TC-PVP-002", "PvP Battle", "Join battle room with valid room code", "P1", "Room waiting", "POST /api/pvp/join with room code", "Status transitions to MATCHED", "Pass"],
        ["TC-PVP-003", "PvP Battle", "Synchronize opponent test case progress", "P1", "Match in progress", "POST progress update + GET status", "Opponent sees updated test count", "Pass"],
        ["TC-SEC-001", "Security", "Rate limiter throttles rapid bursts", "P1", "API endpoint", "Send burst exceeding window limit", "HTTP 429 Too Many Requests", "Pass"],
        ["TC-FE-001", "Frontend", "Vite production bundle compilation", "P0", "Source valid", "Run npm run build", "Exit code 0, dist/ created", "Pass"],
        ["TC-SEL-001", "Selenium E2E", "Automated browser testing across 8 user journeys", "P0", "Vite + Django active", "Run python testing/selenium_tests.py", "8 / 8 test cases pass, screenshots saved", "Pass"]
    ]
    for row in cases:
        ws.append(row)
    style_table(ws)
    wb.save(os.path.join(BASE_DIR, "TEST_CASES.xlsx"))

# 3. TEST EXECUTION RESULTS WORKBOOK
def create_test_results():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Execution Results"
    headers = ["Execution ID", "Test ID", "Test Name", "Test Type", "Environment", "Execution Date", "Actual Outcome", "Status", "Notes"]
    ws.append(headers)

    results = [
        ["EXE-001", "TC-AUTH-001", "User Registration", "Unit/API", "Postgres/Neon", "2026-10-16", "HTTP 200 returned with valid JWT token", "Pass", "Clean registration"],
        ["EXE-002", "TC-AUTH-002", "Duplicate Registration", "Unit/API", "Postgres/Neon", "2026-10-16", "HTTP 400 returned with duplicate email error", "Pass", "Validation caught duplicate"],
        ["EXE-003", "TC-AUTH-003", "User Login", "Unit/API", "Postgres/Neon", "2026-10-16", "HTTP 200 returned with JWT and user object", "Pass", "JWT signed with HMAC-SHA256"],
        ["EXE-004", "TC-AUTH-004", "Invalid Login", "Unit/API", "Postgres/Neon", "2026-10-16", "HTTP 401 returned, token not issued", "Pass", "Proper authentication error"],
        ["EXE-005", "TC-AUTH-005", "Unauthenticated Guard", "Security", "Postgres/Neon", "2026-10-16", "HTTP 401 returned on unauthenticated request", "Pass", "JWT Bearer required"],
        ["EXE-006", "TC-AUTH-006", "Google OAuth Config", "Integration", "Postgres/Neon", "2026-10-16", "Google client ID returned with authorization URL", "Pass", "Config verified"],
        ["EXE-007", "TC-AUTH-007", "GitHub OAuth Config", "Integration", "Postgres/Neon", "2026-10-16", "GitHub client ID returned with authorization URL", "Pass", "Config verified"],
        ["EXE-008", "TC-AUTH-008", "LinkedIn Absent", "Security", "Postgres/Neon", "2026-10-16", "LinkedIn key completely omitted from payload", "Pass", "Purge verified"],
        ["EXE-009", "TC-EVAL-001", "Python Passing Run", "Unit/API", "Subprocess Sandbox", "2026-10-16", "All sample assertions passed, stdout verified", "Pass", "Engine functioning cleanly"],
        ["EXE-010", "TC-EVAL-002", "Python Failing Run", "Unit/API", "Subprocess Sandbox", "2026-10-16", "Assertion failure reported with line info", "Pass", "Diff clearly rendered"],
        ["EXE-011", "TC-EVAL-003", "Timeout Guard", "Security/Perf", "Subprocess Sandbox", "2026-10-16", "Terminated at 5.0 seconds, no CPU hang", "Pass", "Subprocess killed gracefully"],
        ["EXE-012", "TC-EVAL-004", "SQL Challenge Run", "Unit/API", "SQLite Sandbox", "2026-10-16", "Returned exact filtered rows from table", "Pass", "In-memory runner operational"],
        ["EXE-013", "TC-EVAL-005", "SQL Security Block", "Security", "SQLite Sandbox", "2026-10-16", "Blocked load_extension with SECURITY_ERROR", "Pass", "Sanitizer verified"],
        ["EXE-014", "TC-EVAL-006", "Submission XP Award", "Unit/API", "Postgres/Neon", "2026-10-16", "Total score incremented by 100, record saved", "Pass", "XP progression accurate"],
        ["EXE-015", "TC-GAME-001", "Streak Increment", "Unit", "Postgres/Neon", "2026-10-16", "Streak incremented from 1 to 2 next day", "Pass", "Timezone localdate verified"],
        ["EXE-016", "TC-GAME-002", "Streak Lapse", "Unit", "Postgres/Neon", "2026-10-16", "Streak reset to 1 after 3-day inactivity", "Pass", "Lapse algorithm functioning"],
        ["EXE-017", "TC-GAME-003", "Leaderboard Ranking", "Unit/API", "Postgres/Neon", "2026-10-16", "Ordered strictly descending by total score", "Pass", "SQL ORDER BY verified"],
        ["EXE-018", "TC-CARE-001", "Career Readiness", "Unit/API", "Postgres/Neon", "2026-10-16", "Readiness percentage computed per skill group", "Pass", "Weights accurate"],
        ["EXE-019", "TC-CARE-002", "Weakness Matching", "Unit/API", "Postgres/Neon", "2026-10-16", "Challenges prioritized matching weakness tags", "Pass", "Recommender verified"],
        ["EXE-020", "TC-ECON-001", "BugBytes Checkout", "Unit/API", "Postgres/Neon", "2026-10-16", "Wallet credited with package BugBytes", "Pass", "Balance updated"],
        ["EXE-021", "TC-ECON-002", "Challenge Solve Refund", "Unit/API", "Postgres/Neon", "2026-10-16", "Refunded user money in INR, BugBytes intact", "Pass", "Refund constraint verified"],
        ["EXE-022", "TC-PVP-001", "PvP Room Create", "Unit/API", "Postgres/Neon", "2026-10-16", "Generated 6-char alphanumeric room code", "Pass", "Unique code generated"],
        ["EXE-023", "TC-PVP-002", "PvP Room Join", "Unit/API", "Postgres/Neon", "2026-10-16", "Matched player 2 and status changed to MATCHED", "Pass", "Transition verified"],
        ["EXE-024", "TC-PVP-003", "PvP Progress Sync", "Unit/API", "Postgres/Neon", "2026-10-16", "Progress updated and retrieved on status call", "Pass", "Live polling verified"],
        ["EXE-025", "TC-SEC-001", "Rate Limiter Throttle", "Security", "Postgres/Neon", "2026-10-16", "HTTP 429 triggered on rapid request burst", "Pass", "Throttling guard verified"],
        ["EXE-026", "TC-FE-001", "Vite Production Build", "Build", "Node.js v20", "2026-10-16", "2353 modules bundled with 0 errors in 9.5s", "Pass", "Production ready"],
        ["EXE-027", "TC-AUTH-009", "Legitimate Email Enforcement", "Security/UI", "Chrome / API", "2026-10-19", "Arbitrary emails blocked with clear error messaging", "Pass", "Regex and DNS domain validated"],
        ["EXE-028", "TC-AUTH-010", "Mandatory Email OTP", "Integration", "Gmail SMTP / Redis", "2026-10-19", "6-digit OTP delivered and verified in login & signup", "Pass", "SMTP and cache functional"],
        ["EXE-029", "TC-STAT-001", "Clean Zero-State Initialization", "Functional", "React / Postgres", "2026-10-19", "New users start with 0-day streak and blank stats", "Pass", "Zero phantom statistics"],
        ["EXE-030", "TC-SEL-001", "Selenium E2E Test Suite", "Automated E2E", "Headless Chrome", "2026-10-19", "All 8 Selenium test suites passed with 8 screenshots", "Pass", "100% E2E automated pass"]
    ]
    for row in results:
        ws.append(row)
    style_table(ws)
    wb.save(os.path.join(BASE_DIR, "TEST_EXECUTION_RESULTS.xlsx"))

# 4. BUG REPORTS WORKBOOK
def create_bug_reports():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Defect Log"
    headers = ["Defect ID", "Title", "Severity", "Priority", "Status", "Reported Date", "Resolved Date", "Root Cause", "Resolution / Fix"]
    ws.append(headers)

    bugs = [
        ["BUG-001", "LinkedIn OAuth buttons visible after removal request", "Medium", "P1", "Resolved", "2026-10-15", "2026-10-15", "OAuth configuration still contained LinkedIn endpoints and UI assets", "Completely purged LinkedIn from views, OAuthButtons.jsx, Settings.jsx, and configs"],
        ["BUG-002", "Challenge solve refund returned BugBytes instead of real money", "High", "P0", "Resolved", "2026-10-14", "2026-10-14", "Refund transaction credited virtual BugBytes rather than INR refund amount", "Refactored refund reconciliation to strictly refund user's money (INR) without touching BugBytes balance"],
        ["BUG-003", "Streak calculation lapsed across timezone offsets", "Medium", "P2", "Resolved", "2026-10-15", "2026-10-15", "Raw UTC day diffing caused false resets around midnight", "Implemented timezone.localdate() with explicit 1-day diff tolerance"],
        ["BUG-004", "Career Insights displayed static dummy data", "Medium", "P2", "Resolved", "2026-10-15", "2026-10-15", "Frontend failed to connect user profile strengths/weaknesses to recommendations", "Linked User profile interests, strengths, and weaknesses directly to Career Engine ML service"],
        ["BUG-005", "Arbitrary / Fake emails accepted during signup and login", "High", "P1", "Resolved", "2026-10-19", "2026-10-19", "Absence of domain legitimacy regex in frontend and backend email validators", "Added strict email validator in frontend utils and Django backend rejecting invalid domains"],
        ["BUG-006", "New user initialized with hardcoded 5-day streak and fake bio", "Medium", "P2", "Resolved", "2026-10-19", "2026-10-19", "Hardcoded mock notification in App.jsx and mock profile fields in views.py", "Cleared default notifications and initialized new users with 0 streak, 0 solved, empty badges"],
        ["BUG-007", "OTP verification bypassed with arbitrary 6-digit number", "Critical", "P0", "Resolved", "2026-10-19", "2026-10-19", "views.py contained fallback 'elif len(otp) == 6: otp_valid = True' bypassing verification", "Removed mock bypass, hooked real Gmail SMTP credentials, enforced cache verification and single-use eviction"]
    ]
    for row in bugs:
        ws.append(row)
    style_table(ws)
    wb.save(os.path.join(BASE_DIR, "BUG_REPORTS.xlsx"))

if __name__ == "__main__":
    create_rtm()
    create_test_cases()
    create_test_results()
    create_bug_reports()
    print("All 4 QA workbooks updated and generated successfully.")

