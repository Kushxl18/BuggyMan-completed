# BuggyMan Automated Selenium End-to-End (E2E) Test Report

**Document ID:** SEL-REP-2026-v1.0  
**Project:** BuggyMan Software Engineering Lab  
**Harness:** Selenium WebDriver 4.38.0 + Google Chrome (Headless mode)  
**Executed By:** Automated Quality Assurance Suite  
**Date:** October 19, 2026  
**Status:** **100% Passed (8 / 8 Tests OK)**  

---

## 1. Executive Summary

This report documents the execution of the automated browser-level Selenium End-to-End (E2E) test suite for the BuggyMan platform. Testing validates core user journeys including **Authentication Modes**, **Strict Email Format Enforcement**, **Mandatory 6-Digit Email OTP Verification**, **Forgot Password Recovery**, and **Seamless Navigation Flows**.

```
========================================================================================
SELENIUM TEST SUITE EXECUTION SUMMARY
========================================================================================
Test Runner:          Python unittest + Selenium WebDriver 4.38.0
Target Browser:       Google Chrome 155.0.8059.80 (Headless Mode, 1440x900 resolution)
Frontend URL:         http://localhost:3000
Backend API URL:      http://localhost:8000/api
Tests Executed:       8
Tests Passed:         8 (100%)
Tests Failed:         0 (0%)
Execution Time:       21.803 seconds
Visual Evidence:      8 High-Resolution PNG Screenshots Captured in testing/evidence/selenium/
========================================================================================
```

---

## 2. Test Execution Breakdown

| # | Test Case Identifier | Feature Under Test | Expected Behavior | Observed Result | Status | Screenshot Artifact |
|---|---|---|---|---|:---:|---|
| 1 | `test_01_login_page_renders_and_has_both_modes` | Login Interface & Mode Switcher | Renders brand header, inputs, and tabs for "Password Login" and "Email OTP Login". | Mode switcher and inputs fully rendered and interactive. | **PASS** | `01_login_password_mode.png` |
| 2 | `test_02_login_invalid_email_validation` | Email Legitimacy Guard on Login | Submitting malformed email (e.g. `invalid-email@`) triggers immediate client-side error banner. | Error banner displayed: "Please include a valid domain extension...". | **PASS** | `02_login_invalid_email_error.png` |
| 3 | `test_03_login_otp_mode_transition` | Email OTP Instant Login Flow | Switching to OTP mode prompts for email, dispatches 6-digit OTP, and renders code entry with cooldown. | Password input hidden; 6-digit OTP box and resend timer rendered. | **PASS** | `03_login_otp_mode_active.png` |
| 4 | `test_04_signup_step1_renders_mandatory_otp_badge` | Registration Security Indicators | Step 1 displays mandatory OTP notice, email helper warning, and button labeled "Verify Email & Continue". | Security banner, helper text, and 5-step progress bar verified. | **PASS** | `04_signup_step1_badge.png` |
| 5 | `test_05_signup_form_validations` | Registration Input Validation | Rejects empty fields, weak passwords, and illegitimate email formats before dispatching OTP. | Rejection banners correctly display validation instructions. | **PASS** | `05_signup_validations_tested.png` |
| 6 | `test_06_signup_step1_to_step2_otp_transition` | Registration Step 1 $\rightarrow$ Step 2 OTP Transition | Submitting valid Step 1 credentials triggers OTP generation and loads Step 2 (Verify Email). | Transitions to Step 2 screen with 6-digit OTP box, cooldown timer, and edit email link. | **PASS** | `06_signup_step2_otp_screen.png` |
| 7 | `test_07_forgot_password_page_flow` | Password Recovery Verification | Submitting legitimate email advances to Step 2 with verification code input and new password fields. | 6-digit reset code field and dual password fields successfully rendered. | **PASS** | `07_forgot_password_step2.png` |
| 8 | `test_08_navigation_and_cross_links` | Cross-Page Routing & Navigation | Seamless bidirectional navigation between `/login` and `/register`. | URL transitions verified with zero page reload glitches. | **PASS** | `08_navigation_seamless.png` |

---

## 3. Visual Evidence & Artifacts

All screenshots were programmatically captured during the live browser execution and stored in:
`testing/evidence/selenium/`

1. **`01_login_password_mode.png`**: Verifies login form layout and the newly added Password/Email OTP tab switcher.
2. **`02_login_invalid_email_error.png`**: Captures real-time validation error rejecting invalid domain extensions.
3. **`03_login_otp_mode_active.png`**: Shows active Email OTP login interface with 6-digit code entry and countdown timer.
4. **`04_signup_step1_badge.png`**: Confirms registration Step 1 indicators including mandatory OTP notification and 5-step wizard.
5. **`05_signup_validations_tested.png`**: Shows error feedback for empty fields and malformed email inputs.
6. **`06_signup_step2_otp_screen.png`**: Captures Step 2 OTP verification screen with active countdown and edit email link.
7. **`07_forgot_password_step2.png`**: Demonstrates forgot password transition from email input to code entry and password reset.
8. **`08_navigation_seamless.png`**: Confirms routing integrity when toggling between login and signup.

---

## 4. How to Re-Run the Selenium Test Suite

Ensure the Django backend (port 8000) and Vite frontend (port 3000) are running, then execute:

```powershell
python testing/selenium_tests.py
```

*The test runner automatically initializes headless Google Chrome, executes all test cases, saves screenshot evidence, and reports results to stdout.*
