import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class BankServiceUIAndSecurityTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.base_url = "http://localhost:8000"
        cls.wait = WebDriverWait(cls.driver, 10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def test_11_responsive_ui_design(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
            time.sleep(2)
            
            original_size = self.driver.get_window_size()
            
            self.driver.set_window_size(375, 667)
            time.sleep(1)
            
            page_elements = self.driver.find_elements(By.XPATH, "//*")
            self.assertTrue(len(page_elements) > 5)
            
            self.driver.set_window_size(768, 1024)
            time.sleep(1)
            
            page_elements = self.driver.find_elements(By.XPATH, "//*")
            self.assertTrue(len(page_elements) > 5)
            
            self.driver.set_window_size(1920, 1080)
            time.sleep(1)
            
            page_elements = self.driver.find_elements(By.XPATH, "//*")
            self.assertTrue(len(page_elements) > 5)
            
            self.driver.set_window_size(original_size['width'], original_size['height'])
            
        except Exception as e:
            self.fail(f"Responsive UI test failed: {str(e)}")
    
    def test_12_performance_and_response_time(self):
        try:
            start_time = time.time()
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
            load_time = time.time() - start_time
            
            self.assertLess(load_time, 10)
            
            start_time = time.time()
            account_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'account') or contains(text(), 'руб')]"))
            )
            account_button.click()
            
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
            )
            response_time = time.time() - start_time
            
            self.assertLess(response_time, 5)
            
        except Exception as e:
            self.fail(f"Performance test failed: {str(e)}")
    
    def test_13_multiple_clicks_and_rapid_input(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
            time.sleep(2)
            
            account_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'account') or contains(text(), 'руб')]"))
            )
            
            for _ in range(3):
                account_button.click()
                time.sleep(0.1)
            
            card_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or @placeholder]")
            self.assertTrue(len(card_inputs) >= 1)
            
            card_input = card_inputs[0]
            
            for char in "1234567890123456":
                card_input.send_keys(char)
                time.sleep(0.05)
            
            final_value = card_input.get_attribute("value")
            self.assertEqual(len(final_value), 16)
            
        except Exception as e:
            self.fail(f"Multiple clicks test failed: {str(e)}")
    
    def test_14_keyboard_accessibility(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
            time.sleep(2)
            
            actions = ActionChains(self.driver)
            
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.5)
            
            focused_element = self.driver.switch_to.active_element
            self.assertIsNotNone(focused_element)
            
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(1)
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
            )
            
            actions.send_keys("1234567890123456").perform()
            actions.send_keys(Keys.TAB).perform()
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(1)
            
            amount_inputs = self.driver.find_elements(By.XPATH, "//input[@type='number' or @type='text']")
            self.assertTrue(len(amount_inputs) > 0)
            
        except Exception as e:
            self.fail(f"Keyboard accessibility test failed: {str(e)}")
    
    def test_15_data_security_and_storage(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
            time.sleep(2)
            
            account_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'account') or contains(text(), 'руб')]"))
            )
            account_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
            )
            card_input.send_keys("1234567890123456")
            
            local_storage = self.driver.execute_script("return JSON.stringify(localStorage);")
            session_storage = self.driver.execute_script("return JSON.stringify(sessionStorage);")
            
            self.assertNotIn("1234567890123456", local_storage)
            self.assertNotIn("1234567890123456", session_storage)
            
            console_logs = self.driver.get_log('browser')
            
            sensitive_data_in_logs = False
            for log in console_logs:
                if "1234567890123456" in log.get('message', ''):
                    sensitive_data_in_logs = True
                    break
            
            self.assertFalse(sensitive_data_in_logs)
            
            input_type = card_input.get_attribute("type")
            self.assertIn(input_type, ["text", "password", "tel"])
            
        except Exception as e:
            self.fail(f"Data security test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 