import os
import sys
import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from selenium_tests import BuggyManBaseSeleniumTest, FRONTEND_URL

class FeatureArenaE2ETest(BuggyManBaseSeleniumTest):
    def test_feature_arena_complete_workflow(self):
        # 1. Login and Navigate to Feature Challenges Catalog
        self.login_as_qa_user()
        self.driver.get(f"{FRONTEND_URL}/feature-challenges")

        # 2. Verify Catalog Header & Cards Rendered
        header = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Feature Implementation Arena')]"))
        )
        self.assertTrue(header.is_displayed())

        # Verify challenge cards exist
        cards = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//h3[contains(., 'Sliding-Window') or contains(., 'JWT') or contains(., 'Cart')]"))
        )
        self.assertGreaterEqual(len(cards), 1, "Feature challenge cards should be visible")

        # 3. Click Open Codebase Workspace on First Challenge
        open_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Open Codebase Workspace')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", open_btn)
        time.sleep(0.5)
        open_btn.click()

        # 4. Verify Codebase Workspace Elements
        # Verify workspace title and explorer
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Project Repository')]"))
        )
        
        # Verify repository files listed in left panel
        files = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//aside//span[contains(text(), '.py') or contains(text(), '.js')]"))
        )
        self.assertGreaterEqual(len(files), 1, "Repository files must be listed in explorer")

        # Verify Run Tests button exists
        run_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Run Tests')]"))
        )
        self.assertTrue(run_btn.is_displayed())

        # 5. Switch to Assistant Tab
        assistant_tab = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Assistant')]"))
        )
        assistant_tab.click()
        time.sleep(0.5)

        # Verify AI Codebase Assistant is visible
        assistant_welcome = WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'AI CODEBASE ASSISTANT') or contains(text(), 'AI Codebase Assistant')]"))
        )
        self.assertTrue(assistant_welcome.is_displayed())

        # 6. Execute Run Tests
        run_btn.click()
        time.sleep(1)

        # Verify Test Results Drawer displays results
        test_results_header = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Test Results')]"))
        )
        self.assertTrue(test_results_header.is_displayed())

        # 7. Create a New File in Workspace
        new_file_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Create New File']"))
        )
        new_file_btn.click()

        new_file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='app/services/cache.py']"))
        )
        new_file_input.send_keys("app/utils/test_helper.py")

        create_btn = self.driver.find_element(By.XPATH, "//button[text()='Create']")
        create_btn.click()
        time.sleep(1)

        # Verify new file appears in explorer
        new_file_item = WebDriverWait(self.driver, 8).until(
            EC.presence_of_element_located((By.XPATH, "//aside//span[contains(text(), 'test_helper.py')]"))
        )
        self.assertTrue(new_file_item.is_displayed())
        
        self.capture_screenshot("24_feature_arena_verified.png")
        print("Feature Implementation Arena E2E test passed successfully!")

if __name__ == '__main__':
    unittest.main()
