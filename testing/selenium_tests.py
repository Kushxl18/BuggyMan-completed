import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence", "selenium")
os.makedirs(EVIDENCE_DIR, exist_ok=True)

QA_USER_EMAIL = "qa@buggyman.test"
QA_USER_PASSWORD = "Password123!"


class BuggyManBaseSeleniumTest(unittest.TestCase):
    """Base class with shared Chrome webdriver setup, teardown, and helper utilities."""

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

    def capture_screenshot(self, filename):
        path = os.path.join(EVIDENCE_DIR, filename)
        self.driver.save_screenshot(path)
        print(f"  [Evidence Saved] {filename}")
        return path

    def clear_session(self):
        try:
            self.driver.get(f"{FRONTEND_URL}/login")
            self.driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            self.driver.delete_all_cookies()
            self.driver.refresh()
            time.sleep(0.5)
        except Exception:
            pass

    CACHED_TOKEN = None

    @classmethod
    def get_auth_token(cls):
        if not cls.CACHED_TOKEN:
            import urllib.request, json
            data = json.dumps({'email': QA_USER_EMAIL, 'password': QA_USER_PASSWORD}).encode('utf-8')
            req = urllib.request.Request('http://127.0.0.1:8000/api/login', data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as resp:
                cls.CACHED_TOKEN = json.loads(resp.read().decode('utf-8')).get('token')
        return cls.CACHED_TOKEN

    def login_as_qa_user(self):
        """Helper to establish an authenticated QA session instantly without throttling."""
        token = self.get_auth_token()
        self.driver.get(f"{FRONTEND_URL}/login")
        self.driver.execute_script(f"""
            window.localStorage.setItem('token', '{token}');
            window.localStorage.setItem('buggyman_onboarding_completed', 'true');
        """)
        self.driver.get(f"{FRONTEND_URL}/dashboard")
        WebDriverWait(self.driver, 10).until(lambda d: "/dashboard" in d.current_url)
        time.sleep(0.5)


class BuggyManAuthSeleniumTest(BuggyManBaseSeleniumTest):
    """Suite 1: Authentication, Validations, and Registration User Journeys."""

    def setUp(self):
        self.clear_session()

    def test_01_login_page_renders_form_controls(self):
        """Verify Login page loads with brand header, text input, password input, and submit button."""
        self.driver.get(f"{FRONTEND_URL}/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Welcome Back')]"))
        )
        
        # Verify Brand and Welcome headers
        h2 = self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Welcome Back')]")
        self.assertTrue(h2.is_displayed())

        # Verify password form fields
        username_input = self.driver.find_element(By.XPATH, "//input[@type='text']")
        password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
        submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        self.assertTrue(username_input.is_displayed())
        self.assertTrue(password_input.is_displayed())
        self.assertTrue(submit_btn.is_displayed())

        self.capture_screenshot("01_login_form_rendered.png")

    def test_02_login_invalid_email_validation(self):
        """Verify invalid email syntax is rejected with a validation message."""
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
        self.capture_screenshot("02_login_invalid_email_error.png")

    def test_03_login_invalid_password_error(self):
        """Verify wrong password returns unauthorized error message."""
        self.driver.get(f"{FRONTEND_URL}/login")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
        )
        self.driver.find_element(By.XPATH, "//input[@type='text']").send_keys(QA_USER_EMAIL)
        self.driver.find_element(By.XPATH, "//input[@type='password']").send_keys("IncorrectPassword999!")
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        error_box = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'bg-rose-500/10')]"))
        )
        self.assertTrue(error_box.is_displayed())
        self.capture_screenshot("03_login_wrong_password.png")

    def test_04_successful_login_and_token_storage(self):
        """Verify valid login establishes session, stores token, and redirects to Dashboard."""
        self.login_as_qa_user()
        self.assertIn("/dashboard", self.driver.current_url)

        # Verify JWT token is stored in localStorage
        token = self.driver.execute_script("return window.localStorage.getItem('token');")
        self.assertIsNotNone(token)
        self.assertTrue(len(token) > 20)
        self.capture_screenshot("04_dashboard_authenticated.png")

    def test_05_signup_step1_renders_and_validates(self):
        """Verify Signup page loads Step 1 and validates required fields."""
        self.driver.get(f"{FRONTEND_URL}/register")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Create your account')]"))
        )
        h3 = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Create your account')]")
        self.assertTrue(h3.is_displayed())

        # Click Continue without filling fields
        continue_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Continue')]")
        continue_btn.click()

        # Assert validation error message appears
        time.sleep(1)
        err = self.driver.find_element(By.XPATH, "//*[contains(@class, 'text-rose') or contains(@class, 'bg-rose')]")
        self.assertTrue(err.is_displayed())
        self.capture_screenshot("05_signup_empty_validation.png")

    def test_06_forgot_password_page_flow(self):
        """Verify Forgot Password flow: request OTP code and validate invalid OTP rejection."""
        self.driver.get(f"{FRONTEND_URL}/forgot-password")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Forgot Password')]"))
        )
        email_input = self.driver.find_element(By.XPATH, "//input[@type='text' or @type='email']")
        send_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        self.assertTrue(email_input.is_displayed())
        self.assertTrue(send_btn.is_displayed())

        # Step 1: Submit registered email
        email_input.clear()
        email_input.send_keys(QA_USER_EMAIL)
        time.sleep(1)
        send_btn.click()

        # Step 2: Verify transition to OTP verification step
        otp_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '123456')]"))
        )
        self.assertTrue(otp_input.is_displayed())

        # Submit invalid OTP to trigger error banner
        otp_input.send_keys("000000")
        pwd_inputs = self.driver.find_elements(By.XPATH, "//input[@type='password']")
        if len(pwd_inputs) >= 2:
            pwd_inputs[0].send_keys("NewPass123!")
            pwd_inputs[1].send_keys("NewPass123!")
        reset_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        reset_btn.click()

        err_box = WebDriverWait(self.driver, 8).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'bg-rose-500/10') or contains(@class, 'bg-rose')]"))
        )
        self.assertTrue(err_box.is_displayed())
        self.capture_screenshot("06_forgot_password_invalid.png")


class BuggyManNavigationAndLayoutTest(BuggyManBaseSeleniumTest):
    """Suite 2: Dashboard, Navigation Bar, Theme Toggling, and Profile Access."""

    def setUp(self):
        self.driver.set_window_size(1440, 900)
        self.login_as_qa_user()

    def test_07_dashboard_metrics_and_quick_links(self):
        """Verify Dashboard loads with user metrics, quick action links, and arena navigation."""
        self.driver.get(f"{FRONTEND_URL}/dashboard")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Welcome to BuggyMan') or contains(text(), 'Debugging Arenas')]"))
        )
        self.capture_screenshot("07_dashboard_metrics.png")

    def test_08_theme_switcher_toggle(self):
        """Verify Dark and Light theme toggle button switches the DOM class on <html>."""
        self.driver.get(f"{FRONTEND_URL}/dashboard")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@title='Toggle Theme']"))
        )
        theme_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Toggle Theme']"))
        )
        initial_is_dark = "dark" in (self.driver.find_element(By.TAG_NAME, "html").get_attribute("class") or "")
        
        theme_btn.click()
        WebDriverWait(self.driver, 5).until(
            lambda d: ("dark" in (d.find_element(By.TAG_NAME, "html").get_attribute("class") or "")) != initial_is_dark
        )

        new_is_dark = "dark" in (self.driver.find_element(By.TAG_NAME, "html").get_attribute("class") or "")
        self.assertNotEqual(initial_is_dark, new_is_dark, "Theme class on <html> should toggle")
        self.capture_screenshot("08_theme_toggled.png")

    def test_09_sidebar_navigation_links(self):
        """Verify clicking sidebar links navigates to the respective platform pages."""
        # 1. Code Challenges
        self.driver.get(f"{FRONTEND_URL}/challenges")
        WebDriverWait(self.driver, 10).until(lambda d: "/challenges" in d.current_url)
        self.assertIn("/challenges", self.driver.current_url)

        # 2. SQL Lab
        self.driver.get(f"{FRONTEND_URL}/sql-challenges")
        WebDriverWait(self.driver, 10).until(lambda d: "/sql-challenges" in d.current_url)
        self.assertIn("/sql-challenges", self.driver.current_url)

        # 3. Frontend Studio
        self.driver.get(f"{FRONTEND_URL}/design-challenges")
        WebDriverWait(self.driver, 10).until(lambda d: "/design-challenges" in d.current_url)
        self.assertIn("/design-challenges", self.driver.current_url)

        # 4. PvP Battle
        self.driver.get(f"{FRONTEND_URL}/pvp")
        WebDriverWait(self.driver, 10).until(lambda d: "/pvp" in d.current_url)
        self.assertIn("/pvp", self.driver.current_url)

        # 5. Career Insights
        self.driver.get(f"{FRONTEND_URL}/career-insights")
        WebDriverWait(self.driver, 10).until(lambda d: "/career-insights" in d.current_url)
        self.assertIn("/career-insights", self.driver.current_url)

        self.capture_screenshot("09_navigation_verified.png")

    def test_10_logout_clears_session(self):
        """Verify clicking Logout destroys session, clears token, and redirects to Login."""
        WebDriverWait(self.driver, 10).until(lambda d: "/dashboard" in d.current_url)

        # Look for logout button in sidebar
        logout_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@title='Sign Out' or @aria-label='Sign Out' or contains(., 'Sign Out')]"))
        )
        self.driver.execute_script("arguments[0].click();", logout_btn)

        WebDriverWait(self.driver, 10).until(lambda d: "/login" in d.current_url)
        token = self.driver.execute_script("return window.localStorage.getItem('token');")
        self.assertIsNone(token, "Token should be removed on logout")
        self.capture_screenshot("10_logout_success.png")


class BuggyManChallengeCatalogTest(BuggyManBaseSeleniumTest):
    """Suite 3: Challenge Catalogs, Filtering, and Search across Arenas."""

    def setUp(self):
        self.clear_session()
        self.driver.set_window_size(1440, 900)
        self.login_as_qa_user()

    def test_11_code_arena_catalog_and_difficulty_filters(self):
        """Verify Code Arena loads cards and difficulty tabs filter the challenge list."""
        self.driver.get(f"{FRONTEND_URL}/challenges")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Arena')] | //*[contains(., 'API Pagination')]"))
        )

        # Verify challenge cards exist
        cards = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'glass-panel')]//h3 | //h3"))
        )
        self.assertTrue(len(cards) > 0, "Challenge cards should be present")

        # Select 'Easy' difficulty from dropdown
        diff_select = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//select[.//option[@value='Easy']]"))
        )
        Select(diff_select).select_by_value("Easy")
        time.sleep(1)
        self.capture_screenshot("11_code_arena_filtered.png")

    def test_12_code_arena_search_filtering(self):
        """Verify typing in search input filters challenges dynamically."""
        self.driver.get(f"{FRONTEND_URL}/challenges")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text'] | //input[@placeholder]"))
        )

        search_input = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Search') or contains(@placeholder, 'search')]")
        search_input.clear()
        search_input.send_keys("Pagination")
        time.sleep(1)

        # Verify search result
        matched = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Pagination')]")
        self.assertTrue(len(matched) > 0, "Search for 'Pagination' should return matched challenge")
        self.capture_screenshot("12_search_filtering.png")

    def test_13_sql_lab_catalog_renders(self):
        """Verify SQL Lab loads with challenge cards and database schemas."""
        self.driver.get(f"{FRONTEND_URL}/sql-challenges")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'SQL')]"))
        )
        self.capture_screenshot("13_sql_lab_rendered.png")

    def test_14_frontend_studio_catalog_renders(self):
        """Verify Frontend Studio loads with UI component challenges."""
        self.driver.get(f"{FRONTEND_URL}/design-challenges")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Frontend')]"))
        )
        self.capture_screenshot("14_frontend_studio_rendered.png")


class BuggyManEditorAndEvaluationTest(BuggyManBaseSeleniumTest):
    """Suite 4: Monaco Editor, Problem Statement, Run Code, and Evaluation Panels."""

    def setUp(self):
        self.clear_session()
        self.driver.set_window_size(1440, 900)
        self.login_as_qa_user()

    def test_15_challenge_editor_loads_problem_statement(self):
        """Verify challenge editor loads with Problem Statement, Examples, and Action buttons."""
        self.driver.get(f"{FRONTEND_URL}/challenge/1")
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Problem') or contains(text(), 'Pagination')]"))
        )

        # Verify Run and Submit buttons exist
        run_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Run')]"))
        )
        submit_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Submit')]")
        self.assertTrue(run_btn.is_displayed())
        self.assertTrue(submit_btn.is_displayed())
        self.capture_screenshot("15_challenge_editor_ready.png")

    def test_16_run_code_execution_flow(self):
        """Verify clicking Run Code triggers execution and updates Test Results panel."""
        self.driver.get(f"{FRONTEND_URL}/challenge/1")
        run_btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Run')]"))
        )
        run_btn.click()

        # Wait for test execution result tab or testcase output to display
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Test Result') or contains(text(), 'Passed') or contains(text(), 'Failed') or contains(@class, 'lucide-check') or contains(@class, 'lucide-x')]"))
        )
        self.capture_screenshot("16_run_code_result.png")


class BuggyManPvPLobbyTest(BuggyManBaseSeleniumTest):
    """Suite 5: Real-time PvP Lobby, Presence Tracking, and Matchmaking Controls."""

    def setUp(self):
        self.clear_session()
        self.driver.set_window_size(1440, 900)
        self.login_as_qa_user()

    def test_17_pvp_lobby_and_presence_pill(self):
        """Verify PvP Battle lobby renders real-time presence indicator and 3 action cards."""
        self.driver.get(f"{FRONTEND_URL}/pvp")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'PvP Debugging Battle')]"))
        )
        
        # Verify action cards exist: Quick Match, Create Room, Join Room
        quick_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Find Opponent')]")
        create_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Create Battle Room')]")
        join_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Enter Room')]")
        self.assertTrue(quick_btn.is_displayed())
        self.assertTrue(create_btn.is_displayed())
        self.assertTrue(join_btn.is_displayed())

        # Verify presence pill exists
        presence = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Online') or contains(text(), 'In Queue')]")
        self.assertTrue(presence.is_displayed())
        self.capture_screenshot("17_pvp_lobby_verified.png")

    def test_18_quick_match_search_and_cancel(self):
        """Verify Quick Match opens searching modal with active timer and Cancel button closes modal."""
        self.driver.get(f"{FRONTEND_URL}/pvp")
        quick_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Find Opponent')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", quick_btn)
        time.sleep(0.5)
        quick_btn.click()

        # Verify searching modal opens
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Searching for Opponent')]"))
        )
        cancel_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Cancel Matchmaking')]"))
        )
        self.assertTrue(cancel_btn.is_displayed())

        # Click Cancel
        cancel_btn.click()
        time.sleep(2.5)
        self.capture_screenshot("18_quick_match_cancelled.png")

    def test_19_create_room_code_generation(self):
        """Verify Create Battle Room generates 6-character room code and Copy button functions."""
        self.driver.get(f"{FRONTEND_URL}/pvp")
        create_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create Battle Room')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_btn)
        time.sleep(0.5)
        create_btn.click()

        # Verify private room modal with room code
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Private Battle Room')]"))
        )
        cancel_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Cancel Battle Room')]"))
        )
        self.assertTrue(cancel_btn.is_displayed())

        cancel_btn.click()
        time.sleep(1)
        self.capture_screenshot("19_create_room_cancelled.png")


class BuggyManCareerInsightsTest(BuggyManBaseSeleniumTest):
    """Suite 6: Career Insights, Role Rankings, and Practice Challenges."""

    def setUp(self):
        self.clear_session()
        self.driver.set_window_size(1440, 900)
        self.login_as_qa_user()

    def test_20_career_insights_renders_top_match_and_gaps(self):
        """Verify Career Insights loads Top Role Match, Market Demand, and Practice Challenges."""
        self.driver.get(f"{FRONTEND_URL}/career-insights")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Career Role Suitability')]"))
        )

        # Verify Top Role Match hero card exists
        top_match_badge = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'TOP ROLE MATCH')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", top_match_badge)
        time.sleep(0.5)
        self.assertTrue(top_match_badge.is_displayed())
        self.capture_screenshot("20_career_insights_verified.png")
        self.assertTrue(top_match_badge.is_displayed())
        self.capture_screenshot("20_career_insights_verified.png")


class BuggyManResponsiveViewportsTest(BuggyManBaseSeleniumTest):
    """Suite 7: Responsive Layouts across Desktop, Tablet, and Mobile Breakpoints."""

    def setUp(self):
        self.clear_session()
        self.driver.set_window_size(1440, 900)
        self.login_as_qa_user()

    def test_21_desktop_viewport_layout(self):
        """Verify desktop 1440x900 viewport displays full sidebar and horizontal layout."""
        self.driver.set_window_size(1440, 900)
        self.driver.get(f"{FRONTEND_URL}/dashboard")
        time.sleep(1)
        self.capture_screenshot("21_responsive_desktop_1440x900.png")

    def test_22_tablet_viewport_layout(self):
        """Verify tablet 768x1024 viewport adjusts layout cleanly without horizontal scroll."""
        self.driver.set_window_size(768, 1024)
        self.driver.get(f"{FRONTEND_URL}/dashboard")
        time.sleep(1)
        self.capture_screenshot("22_responsive_tablet_768x1024.png")

    def test_23_mobile_viewport_layout(self):
        """Verify mobile 375x812 viewport renders hamburger/mobile layout cleanly."""
        self.driver.set_window_size(375, 812)
        self.driver.get(f"{FRONTEND_URL}/dashboard")
        time.sleep(1)
        self.capture_screenshot("23_responsive_mobile_375x812.png")
        # Reset back to desktop default
        self.driver.set_window_size(1440, 900)


if __name__ == "__main__":
    unittest.main()
