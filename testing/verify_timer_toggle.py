import os
import sys
import time
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from selenium_tests import BuggyManBaseSeleniumTest, FRONTEND_URL

class TestTimerPlayPause(BuggyManBaseSeleniumTest):
    def test_timer_play_pause_functionality(self):
        self.login_as_qa_user()
        
        # Navigate to a challenge editor
        self.driver.get(f"{FRONTEND_URL}/challenge/1")
        
        # Locate the timer button
        timer_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-testid='timer-toggle-btn' or contains(@title, 'Timer')]"))
        )
        self.assertIsNotNone(timer_btn)
        
        initial_title = timer_btn.get_attribute('title')
        self.assertIn('Click to Pause Timer', initial_title)
        
        # Wait a moment to see time increment
        time.sleep(2)
        initial_text = timer_btn.text
        
        # Click to pause
        timer_btn.click()
        time.sleep(0.5)
        
        # Assert paused state
        paused_title = timer_btn.get_attribute('title')
        self.assertIn('Click to Resume Timer', paused_title)
        self.assertIn('PAUSED', timer_btn.text.upper())
        
        paused_time_text = timer_btn.text
        # Wait 2 seconds while paused to ensure no time increment
        time.sleep(2)
        self.assertEqual(paused_time_text, timer_btn.text)
        
        # Click to resume
        timer_btn.click()
        time.sleep(0.5)
        resumed_title = timer_btn.get_attribute('title')
        self.assertIn('Click to Pause Timer', resumed_title)
        self.assertNotIn('PAUSED', timer_btn.text.upper())
        print("Timer play/pause verification test passed successfully!")

if __name__ == '__main__':
    unittest.main()
