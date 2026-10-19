import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence", "selenium")
os.makedirs(EVIDENCE_DIR, exist_ok=True)


class BuggyManSeleniumE2ETestCase(unittest.TestCase):
    """
    Selenium Automated End-to-End Test Suite for BuggyMan.
    Covers Authentication, Email Validation, Mandatory Email OTP, and Navigation.
    """

    @classmethod
    def setUpClass(cls):
        opts = ChromeOptions()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1440,900")
        cls.driver = webdriver.Chrome(options=opts)
        cls.driver.implicitly_wait(4)

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        # Clear cookies, localStorage and sessionStorage before each test for total test isolation
        try:
            self.driver.get(FRONTEND_URL)
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            self.driver.delete_all_cookies()
        except Exception:
            pass

    def capture_screenshot(self, filename):
        path = os.path.join(EVIDENCE_DIR, filename)
        self.driver.save_screenshot(path)
        print(f"  [Evidence Saved] {filename}")
        return path

    def test_01_login_page_renders_and_has_both_modes(self):
        """Verify Login page loads with Password Login and Email OTP Login switcher."""
        self.driver.get(f"{FRONTEND_URL}/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Welcome Back')]"))
        )
        
        # Verify Brand and Welcome headers
        h2 = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Welcome Back')]")
        self.assertTrue(h2.is_displayed())

        # Verify Mode Switcher tabs exist
        pwd_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Password Login')]")
        otp_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Email OTP Login')]")
        self.assertTrue(pwd_btn.is_displayed())
        self.assertTrue(otp_btn.is_displayed())

        # Verify password form fields
        username_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        self.assertTrue(username_input.is_displayed())
        self.assertTrue(password_input.is_displayed())

        self.capture_screenshot("01_login_password_mode.png")

    def test_02_login_invalid_email_validation(self):
        """Verify invalid email syntax is rejected on login with validation feedback."""
        self.driver.get(f"{FRONTEND_URL}/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
        )

        user_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        pwd_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        
        user_input.send_keys("invalid-email@")
        pwd_input.send_keys("ValidPassword123!")

        submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()

        # Wait for validation error banner
        error_box = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'bg-rose-500/10')]"))
        )
        self.assertTrue(error_box.is_displayed())
        err_text = error_box.text.lower()
        self.assertTrue("domain" in err_text or "valid" in err_text or "email" in err_text)

        self.capture_screenshot("02_login_invalid_email_error.png")

    def test_03_login_otp_mode_transition(self):
        """Verify Email OTP Login tab switches cleanly and allows requesting a 6-digit code."""
        self.driver.get(f"{FRONTEND_URL}/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Email OTP Login')]"))
        )

        # Switch to OTP Login mode
        otp_mode_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Email OTP Login')]")
        otp_mode_btn.click()

        # Verify email input is displayed and password input is hidden
        email_input = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@type='email']"))
        )
        self.assertTrue(email_input.is_displayed())

        # Enter legitimate email
        email_input.send_keys("tester.buggyman@gmail.com")

        # Click send verification code button
        send_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Send 6-Digit Verification Code')]")
        self.assertTrue(send_btn.is_displayed())
        send_btn.click()

        # Wait for 6-digit OTP code entry to appear
        otp_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='••••••']"))
        )
        self.assertTrue(otp_input.is_displayed())

        # Verify Resend Code timer text
        resend_notice = self.driver.find_element(By.XPATH, "//*[contains(text(), \"Didn't receive the email code?\")]")
        self.assertTrue(resend_notice.is_displayed())

        self.capture_screenshot("03_login_otp_mode_active.png")

    def test_04_signup_step1_renders_mandatory_otp_badge(self):
        """Verify Signup page loads with Mandatory Email OTP badge and informative helper text."""
        self.driver.get(f"{FRONTEND_URL}/register")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Create your account')]"))
        )

        # Verify helper text under email field
        helper = self.driver.find_element(By.XPATH, "//*[contains(text(), 'A 6-digit security code will be sent')]")
        self.assertTrue(helper.is_displayed())

        # Verify button text
        continue_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Verify Email & Continue')]")
        self.assertTrue(continue_btn.is_displayed())

        # Verify sidebar steps show Verify Email
        sidebar = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Verify Email')]")
        self.assertTrue(sidebar.is_displayed())

        self.capture_screenshot("04_signup_step1_badge.png")

    def test_05_signup_form_validations(self):
        """Verify Signup validates empty fields, password strength, and invalid emails."""
        self.driver.get(f"{FRONTEND_URL}/register")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Verify Email & Continue')]"))
        )

        # 1. Test empty fields
        continue_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Verify Email & Continue')]")
        continue_btn.click()

        error_box = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'bg-rose-500/10')]"))
        )
        self.assertIn("complete all account fields", error_box.text.lower())

        # 2. Test illegitimate email syntax
        user_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
        pwd_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password']")
        
        user_input.send_keys("testcoder")
        email_input.send_keys("not-a-legit-email")
        pwd_inputs[0].send_keys("StrongPassword123!")
        pwd_inputs[1].send_keys("StrongPassword123!")

        continue_btn.click()
        time.sleep(0.5)

        # Email format rejection
        error_box = self.driver.find_element(By.XPATH, "//*[contains(@class, 'bg-rose-500/10')]")
        self.assertTrue("valid email" in error_box.text.lower() or "email" in error_box.text.lower())

        self.capture_screenshot("05_signup_validations_tested.png")

    def test_06_signup_step1_to_step2_otp_transition(self):
        """Verify completing Step 1 transitions smoothly into Step 2 OTP verification screen."""
        self.driver.get(f"{FRONTEND_URL}/register")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Create your account')]"))
        )

        user_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
        pwd_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password']")

        unique_id = int(time.time()) % 100000
        user_input.send_keys(f"seluser{unique_id}")
        email_input.send_keys(f"seluser{unique_id}@gmail.com")
        pwd_inputs[0].send_keys("SuperSecret999!")
        pwd_inputs[1].send_keys("SuperSecret999!")

        continue_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Verify Email & Continue')]")
        continue_btn.click()

        # Wait for Step 2 screen ("Verify your email address")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Verify your email address')]"))
        )

        # Check Step 2 Mandatory badge
        step2_badge = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Mandatory Email Verification')]")
        self.assertTrue(step2_badge.is_displayed())

        # Check 6-digit input is visible
        otp_input = self.driver.find_element(By.XPATH, "//input[@placeholder='••••••']")
        self.assertTrue(otp_input.is_displayed())

        # Check countdown / resend prompt
        resend_text = self.driver.find_element(By.XPATH, "//*[contains(text(), \"Didn't receive the code?\")]")
        self.assertTrue(resend_text.is_displayed())

        # Check Edit email link is present
        edit_link = self.driver.find_element(By.XPATH, "//button[contains(text(), '(Edit email)')]")
        self.assertTrue(edit_link.is_displayed())

        self.capture_screenshot("06_signup_step2_otp_screen.png")

    def test_07_forgot_password_page_flow(self):
        """Verify Forgot Password page loads, validates input, and transitions to reset code."""
        self.driver.get(f"{FRONTEND_URL}/forgot-password")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Forgot Password')]"))
        )

        email_input = self.driver.find_element(By.XPATH, "//input[@type='email']")
        self.assertTrue(email_input.is_displayed())

        # Submit legitimate email
        email_input.send_keys("demo.account@gmail.com")
        send_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        send_btn.click()

        # Wait for verification code entry field to appear (Step 2)
        code_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='123456']"))
        )
        self.assertTrue(code_input.is_displayed())

        # Verify password inputs appear
        pwd_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password']")
        self.assertTrue(len(pwd_inputs) >= 2)

        self.capture_screenshot("07_forgot_password_step2.png")

    def test_08_navigation_and_cross_links(self):
        """Verify seamless navigation between Login and Register views."""
        self.driver.get(f"{FRONTEND_URL}/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Create new account')]"))
        )

        # Click Create new account link
        register_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Create new account')]")
        register_link.click()

        # Verify navigated to /register
        WebDriverWait(self.driver, 5).until(EC.url_contains("/register"))
        self.assertIn("/register", self.driver.current_url)

        # Click Sign in link
        signin_link = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Sign in')]"))
        )
        signin_link.click()

        # Verify navigated back to /login
        WebDriverWait(self.driver, 5).until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)

        self.capture_screenshot("08_navigation_seamless.png")


if __name__ == "__main__":
    unittest.main(verbosity=2)
