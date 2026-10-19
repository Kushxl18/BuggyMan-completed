import os
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Color Palette for Excel Styling
HEADER_FILL = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="F8FAFC")
BORDER_THIN = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)
PASS_FILL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
PASS_FONT = Font(name="Calibri", size=10, bold=True, color="166534")
RESOLVED_FILL = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
RESOLVED_FONT = Font(name="Calibri", size=10, bold=True, color="0369A1")


def style_sheet(ws):
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
                val = str(cell.value or '')
                if val in ("Pass", "Passed", "Done", "Closed", "Resolved"):
                    cell.fill = PASS_FILL if val in ("Pass", "Passed") else RESOLVED_FILL
                    cell.font = PASS_FONT if val in ("Pass", "Passed") else RESOLVED_FONT
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif cell.column in (1, 2, 5, 6, 8, 9, 10):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 48)
    ws.row_dimensions[1].height = 28


JIRA_ISSUES = [
    # EPICS
    {
        "Issue Type": "Epic",
        "Issue Key": "BM-EPIC-01",
        "Summary": "Authentication, Identity & Email Security Framework",
        "Description": "Comprehensive security and identity management for BuggyMan, establishing strict email legitimacy, multi-mode authentication, and mandatory OTP verification.",
        "Priority": "Highest",
        "Status": "Done",
        "Component": "Authentication",
        "Epic Link": "",
        "Reporter": "QA Lead",
        "Assignee": "Backend Team",
        "Resolution": "Done",
        "Labels": "security, auth, email, sprint-3"
    },
    {
        "Issue Type": "Epic",
        "Issue Key": "BM-EPIC-02",
        "Summary": "Gamification Data Integrity & Clean State Assurance",
        "Description": "Ensures that newly registered accounts start with clean, unearned stats (0 streak, 0 bugs solved, empty badges) and prevents ghost data.",
        "Priority": "High",
        "Status": "Done",
        "Component": "Gamification",
        "Epic Link": "",
        "Reporter": "QA Lead",
        "Assignee": "Full-Stack Team",
        "Resolution": "Done",
        "Labels": "gamification, streak, profile, sprint-3"
    },
    {
        "Issue Type": "Epic",
        "Issue Key": "BM-EPIC-03",
        "Summary": "Automated End-to-End Regression Test Architecture",
        "Description": "Development and continuous execution of browser-level Selenium automation suite covering critical user flows and regression guards.",
        "Priority": "High",
        "Status": "Done",
        "Component": "Testing",
        "Epic Link": "",
        "Reporter": "QA Lead",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, automation, e2e, regression"
    },

    # USER STORIES
    {
        "Issue Type": "Story",
        "Issue Key": "BM-STORY-01",
        "Summary": "As a platform, I must reject non-legitimate and arbitrary email addresses",
        "Description": "Users must only be allowed to register or login with legitimate emails containing valid domain extensions (.com, .edu, .org) adhering to RFC 5322 rules.",
        "Priority": "Highest",
        "Status": "Done",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "Product Owner",
        "Assignee": "Backend Developer",
        "Resolution": "Done",
        "Labels": "email-validation, security"
    },
    {
        "Issue Type": "Story",
        "Issue Key": "BM-STORY-02",
        "Summary": "As a new user, I must verify my email via a 6-digit OTP before account creation",
        "Description": "Registration requires entering a 6-digit verification code delivered directly to the user's Gmail inbox via live SMTP to prevent phantom accounts.",
        "Priority": "Highest",
        "Status": "Done",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "Product Owner",
        "Assignee": "Full-Stack Developer",
        "Resolution": "Done",
        "Labels": "otp, smtp, gmail, registration"
    },
    {
        "Issue Type": "Story",
        "Issue Key": "BM-STORY-03",
        "Summary": "As a newly registered user, my profile must initialize with 0 streak and no phantom stats",
        "Description": "Prevent new users from showing 5-day streaks, 780 XP, pre-awarded badges, or Jane Doe dummy bio and college information upon initial creation.",
        "Priority": "High",
        "Status": "Done",
        "Component": "Gamification",
        "Epic Link": "BM-EPIC-02",
        "Reporter": "Product Owner",
        "Assignee": "Backend Developer",
        "Resolution": "Done",
        "Labels": "profile, streak, data-integrity"
    },
    {
        "Issue Type": "Story",
        "Issue Key": "BM-STORY-04",
        "Summary": "As a returning user, I want the option to sign in using Email OTP or Password",
        "Description": "The login page provides a dual-mode switcher allowing users to either enter password or request a 6-digit one-time passcode to sign in.",
        "Priority": "High",
        "Status": "Done",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "UX Designer",
        "Assignee": "Frontend Developer",
        "Resolution": "Done",
        "Labels": "login, otp-login, ui"
    },
    {
        "Issue Type": "Story",
        "Issue Key": "BM-STORY-05",
        "Summary": "As an existing user, I want to reset my password using an email verification code",
        "Description": "Forgot password endpoint sends a 6-digit OTP code with 10-minute expiry to user's registered email, verifying it before resetting password.",
        "Priority": "High",
        "Status": "Done",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "Product Owner",
        "Assignee": "Backend Developer",
        "Resolution": "Done",
        "Labels": "forgot-password, security, otp"
    },
    {
        "Issue Type": "Story",
        "Issue Key": "BM-STORY-06",
        "Summary": "As a QA engineer, I want automated Selenium browser testing covering critical paths",
        "Description": "Automated headless Chrome test runner to continuously verify login, signup wizard, OTP entry, password reset, and cross-navigation.",
        "Priority": "High",
        "Status": "Done",
        "Component": "Testing",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Lead",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, chrome"
    },

    # JIRA TEST CASES
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-01",
        "Summary": "Verify legitimate email syntax enforcement on registration",
        "Description": "Submit valid emails (user@gmail.com, student@mit.edu) and verify acceptance. Submit invalid inputs (not-an-email, user@localhost) and verify 400 Bad Request.",
        "Priority": "Highest",
        "Status": "Passed",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Engineer",
        "Assignee": "QA Engineer",
        "Resolution": "Done",
        "Labels": "test-case, backend-unit"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-02",
        "Summary": "Verify mandatory OTP generation and live Gmail SMTP delivery",
        "Description": "Call /api/auth/otp/send with legitimate email. Verify 6-digit OTP stored in Django cache and real email delivered to Gmail inbox via TLS port 587.",
        "Priority": "Highest",
        "Status": "Passed",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Engineer",
        "Assignee": "QA Engineer",
        "Resolution": "Done",
        "Labels": "test-case, integration, smtp"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-03",
        "Summary": "Verify registration with invalid OTP is strictly rejected",
        "Description": "Attempt /api/auth/otp/register with random 6-digit code. Verify HTTP 400 error 'Valid verification code is required'.",
        "Priority": "Highest",
        "Status": "Passed",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Engineer",
        "Assignee": "QA Engineer",
        "Resolution": "Done",
        "Labels": "test-case, negative, security"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-04",
        "Summary": "Verify OTP replay prevention after successful registration",
        "Description": "Register successfully with valid OTP. Attempt immediate second registration using identical OTP. Verify HTTP 400 rejection due to cache eviction.",
        "Priority": "High",
        "Status": "Passed",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Engineer",
        "Assignee": "QA Engineer",
        "Resolution": "Done",
        "Labels": "test-case, security, replay-attack"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-05",
        "Summary": "Verify new user starts with 0-day streak, 0 solved bugs, and empty badges",
        "Description": "Inspect returned user profile JSON after new registration. Assert streak=0, challenges_solved=0, total_score=0, badges=[], college='', bio=''.",
        "Priority": "High",
        "Status": "Passed",
        "Component": "Gamification",
        "Epic Link": "BM-EPIC-02",
        "Reporter": "QA Engineer",
        "Assignee": "QA Engineer",
        "Resolution": "Done",
        "Labels": "test-case, data-integrity"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-06",
        "Summary": "Verify Forgot Password request and reset flow via 6-digit OTP",
        "Description": "Call /api/forgot-password/request, verify OTP code generated. Attempt reset with wrong OTP (400). Reset with correct OTP (200), verify login with new password.",
        "Priority": "High",
        "Status": "Passed",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Engineer",
        "Assignee": "QA Engineer",
        "Resolution": "Done",
        "Labels": "test-case, auth, reset"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-07",
        "Summary": "[Selenium E2E] Verify Login page mode switcher between Password and Email OTP",
        "Description": "Headless Chrome opens /login. Verify tab switcher toggles between password form and email OTP form with 6-digit code entry.",
        "Priority": "High",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, ui"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-08",
        "Summary": "[Selenium E2E] Verify real-time client-side email format validation on Login",
        "Description": "Headless Chrome enters 'invalid-email@' on login form. Click Submit. Verify error banner 'Please include a valid domain extension'.",
        "Priority": "Medium",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, validation"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-09",
        "Summary": "[Selenium E2E] Verify Signup Step 1 renders Mandatory OTP badge and helper text",
        "Description": "Headless Chrome loads /register. Verify Mandatory Email OTP badge, security helper notice, and 'Verify Email & Continue' button.",
        "Priority": "High",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, ui"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-10",
        "Summary": "[Selenium E2E] Verify Signup form validation guards",
        "Description": "Headless Chrome submits empty fields -> verifies error. Submits invalid email syntax -> verifies domain format error.",
        "Priority": "Medium",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, validation"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-11",
        "Summary": "[Selenium E2E] Verify Signup Step 1 transitions smoothly to Step 2 OTP verification",
        "Description": "Headless Chrome fills valid Step 1 credentials, clicks Continue. Verifies transition to Step 2 screen with 6-digit code box and cooldown timer.",
        "Priority": "High",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, flow"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-12",
        "Summary": "[Selenium E2E] Verify Forgot Password transition from email to reset code entry",
        "Description": "Headless Chrome loads /forgot-password, submits legitimate email, verifies transition to Step 2 with code entry and dual password fields.",
        "Priority": "Medium",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, flow"
    },
    {
        "Issue Type": "Test",
        "Issue Key": "BM-TEST-13",
        "Summary": "[Selenium E2E] Verify bidirectional routing between /login and /register",
        "Description": "Headless Chrome navigates login -> register -> login via interactive cross-links, asserting URL transitions.",
        "Priority": "Low",
        "Status": "Passed",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-03",
        "Reporter": "QA Automation Engineer",
        "Assignee": "QA Automation Engineer",
        "Resolution": "Done",
        "Labels": "selenium, e2e, routing"
    },

    # JIRA DEFECT BUG TICKETS
    {
        "Issue Type": "Bug",
        "Issue Key": "BM-BUG-01",
        "Summary": "Arbitrary and non-existent email addresses accepted during login and registration",
        "Description": "The auth system accepted malformed or arbitrary strings without domain checks, permitting non-existent accounts like 'bainjnjdn@gmail.com'. Fixed with RFC 5322 regex and Django EmailValidator.",
        "Priority": "Highest",
        "Status": "Resolved",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "User / QA",
        "Assignee": "Backend Developer",
        "Resolution": "Fixed",
        "Labels": "bug, security, email, resolved"
    },
    {
        "Issue Type": "Bug",
        "Issue Key": "BM-BUG-02",
        "Summary": "Brand new registered accounts displayed phantom 5-day streak and Jane Doe bio",
        "Description": "User model defaults and mock layer assigned static stats (5-day streak, 780 XP, pre-awarded badge, State Technical University) to new accounts. Fixed with strict zero-state defaults.",
        "Priority": "High",
        "Status": "Resolved",
        "Component": "Gamification",
        "Epic Link": "BM-EPIC-02",
        "Reporter": "User / QA",
        "Assignee": "Backend Developer",
        "Resolution": "Fixed",
        "Labels": "bug, streak, profile, resolved"
    },
    {
        "Issue Type": "Bug",
        "Issue Key": "BM-BUG-03",
        "Summary": "OTP registration endpoint permitted bypass with arbitrary 6-digit number",
        "Description": "register_with_otp_view contained 'elif len(otp) == 6: otp_valid = True', allowing any 6-digit number to bypass authentication. Fixed by strictly verifying cache and session OTP.",
        "Priority": "Highest",
        "Status": "Resolved",
        "Component": "Authentication",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Lead",
        "Assignee": "Backend Developer",
        "Resolution": "Fixed",
        "Labels": "bug, security, bypass, resolved"
    },
    {
        "Issue Type": "Bug",
        "Issue Key": "BM-BUG-04",
        "Summary": "Login page lacked Email OTP option despite backend endpoint availability",
        "Description": "Frontend Login.jsx only allowed password submission with no way for users to log in via one-time passcode. Fixed by adding Password / Email OTP dual-mode switcher.",
        "Priority": "Medium",
        "Status": "Resolved",
        "Component": "Frontend UI",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Lead",
        "Assignee": "Frontend Developer",
        "Resolution": "Fixed",
        "Labels": "bug, ui, login, resolved"
    },
    {
        "Issue Type": "Bug",
        "Issue Key": "BM-BUG-05",
        "Summary": "Forgot password URL routes missing in backend/buggyman/urls.py",
        "Description": "Views forgot_password_request_view and forgot_password_reset_view existed in views.py but endpoints returned 404 due to missing url patterns. Fixed by registering routes in urls.py.",
        "Priority": "High",
        "Status": "Resolved",
        "Component": "Backend Routing",
        "Epic Link": "BM-EPIC-01",
        "Reporter": "QA Lead",
        "Assignee": "Backend Developer",
        "Resolution": "Fixed",
        "Labels": "bug, routing, api, resolved"
    }
]


def generate_jira_csv():
    csv_path = os.path.join(BASE_DIR, "JIRA_TEST_EXPORT.csv")
    fieldnames = [
        "Issue Type", "Issue Key", "Summary", "Description", "Priority",
        "Status", "Component", "Epic Link", "Reporter", "Assignee",
        "Resolution", "Labels"
    ]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for issue in JIRA_ISSUES:
            writer.writerow(issue)
    print(f"[Generated] {csv_path} ({len(JIRA_ISSUES)} Jira Issues)")


def generate_jira_excel():
    xlsx_path = os.path.join(BASE_DIR, "JIRA_TEST_MANAGEMENT.xlsx")
    wb = openpyxl.Workbook()

    # Sheet 1: Jira Issues Log
    ws1 = wb.active
    ws1.title = "Jira Backlog & Test Cases"
    headers = [
        "Issue Type", "Issue Key", "Summary", "Description", "Priority",
        "Status", "Component", "Epic Link", "Reporter", "Assignee",
        "Resolution", "Labels"
    ]
    ws1.append(headers)
    for issue in JIRA_ISSUES:
        ws1.append([issue[h] for h in headers])
    style_sheet(ws1)

    # Sheet 2: Defect Tracking Matrix
    ws2 = wb.create_sheet(title="Defect Bug Matrix")
    bug_headers = ["Bug ID", "Summary", "Severity", "Status", "Resolution", "Component", "Root Cause & Fix"]
    ws2.append(bug_headers)
    bugs = [i for i in JIRA_ISSUES if i["Issue Type"] == "Bug"]
    for b in bugs:
        ws2.append([
            b["Issue Key"], b["Summary"], b["Priority"], b["Status"],
            b["Resolution"], b["Component"], b["Description"]
        ])
    style_sheet(ws2)

    # Sheet 3: Execution Metrics Dashboard
    ws3 = wb.create_sheet(title="Jira QA Metrics")
    ws3.append(["Metric Name", "Value", "Status / Target", "Notes"])
    ws3.append(["Total Jira Epics", 3, "Completed", "Auth, Gamification, Automation"])
    ws3.append(["Total User Stories", 6, "100% Done", "All acceptance criteria verified"])
    ws3.append(["Total Test Cases in Jira", 13, "100% Passed", "13 Passed, 0 Failed"])
    ws3.append(["Total Bugs Logged", 5, "100% Resolved", "All 5 critical/high bugs fixed"])
    ws3.append(["Test Execution Pass Rate", "100%", "Target: >= 95%", "Exceeded QA benchmark"])
    ws3.append(["Defect Resolution Rate", "100%", "Target: 100%", "Zero open blockers"])
    style_sheet(ws3)

    wb.save(xlsx_path)
    print(f"[Generated] {xlsx_path} (3 Detailed QA Worksheets)")


if __name__ == "__main__":
    generate_jira_csv()
    generate_jira_excel()
