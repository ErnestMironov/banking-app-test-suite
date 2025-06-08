import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class BankServiceBoundaryTests(unittest.TestCase):
    
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
    
    def test_06_boundary_balance_values(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=0&reserved=0")
            time.sleep(2)
            
            balance_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '0')]")
            self.assertTrue(len(balance_elements) > 0)
            
            self.driver.get(f"{self.base_url}/?balance=1&reserved=0")
            time.sleep(2)
            
            balance_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '1')]")
            self.assertTrue(len(balance_elements) > 0)
            
            self.driver.get(f"{self.base_url}/?balance=999999&reserved=0")
            time.sleep(2)
            
            balance_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '999') or contains(text(), '999999')]")
            self.assertTrue(len(balance_elements) > 0)
            
        except Exception as e:
            self.fail(f"Boundary balance values test failed: {str(e)}")
    
    def test_07_card_number_validation_boundary_cases(self):
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
            
            card_input.clear()
            card_input.send_keys("12345678901234567890")
            time.sleep(1)
            
            current_value = card_input.get_attribute("value")
            self.assertTrue(len(current_value) <= 16)
            
            card_input.clear()
            card_input.send_keys("1234abcd56789012")
            time.sleep(1)
            
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Подтвердить') or contains(text(), 'Далее')]")
            confirm_button.click()
            time.sleep(1)
            
            amount_inputs = self.driver.find_elements(By.XPATH, "//input[@type='number']")
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'ошибка') or contains(@class, 'error')]")
            
            self.assertTrue(len(amount_inputs) == 0 or len(error_elements) > 0)
            
        except Exception as e:
            self.fail(f"Card number boundary validation test failed: {str(e)}")
    
    def test_08_commission_calculation_rounding_down(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=10000&reserved=0")
            time.sleep(2)
            
            account_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'account') or contains(text(), 'руб')]"))
            )
            account_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Подтвердить') or contains(text(), 'Далее')]")
            confirm_button.click()
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='number' or @type='text']"))
            )
            amount_input.clear()
            amount_input.send_keys("55")
            
            time.sleep(2)
            
            commission_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '5') and not(contains(text(), '5.5'))]")
            self.assertTrue(len(commission_elements) > 0)
            
            amount_input.clear()
            amount_input.send_keys("199")
            time.sleep(2)
            
            commission_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '19') and not(contains(text(), '19.9'))]")
            self.assertTrue(len(commission_elements) > 0)
            
        except Exception as e:
            self.fail(f"Commission rounding test failed: {str(e)}")
    
    def test_09_transfer_equal_to_available_amount(self):
        try:
            self.driver.get(f"{self.base_url}/?balance=10000&reserved=0")
            time.sleep(2)
            
            account_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'account') or contains(text(), 'руб')]"))
            )
            account_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Подтвердить') or contains(text(), 'Далее')]")
            confirm_button.click()
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='number' or @type='text']"))
            )
            amount_input.clear()
            amount_input.send_keys("9090")
            
            time.sleep(2)
            
            transfer_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Перевести')]")
            self.assertTrue(len(transfer_buttons) > 0)
            
            amount_input.clear()
            amount_input.send_keys("9091")
            time.sleep(2)
            
            transfer_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Перевести')]")
            error_messages = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'невозможен')]")
            
            self.assertTrue(len(transfer_buttons) > 0 or len(error_messages) > 0)
            
        except Exception as e:
            self.fail(f"Equal amount transfer test failed: {str(e)}")
    
    def test_10_url_parameters_validation(self):
        try:
            self.driver.get(f"{self.base_url}")
            time.sleep(2)
            
            page_elements = self.driver.find_elements(By.XPATH, "//*")
            self.assertTrue(len(page_elements) > 5)
            
            self.driver.get(f"{self.base_url}/?balance=abc&reserved=def")
            time.sleep(2)
            
            page_elements = self.driver.find_elements(By.XPATH, "//*")
            self.assertTrue(len(page_elements) > 5)
            
            self.driver.get(f"{self.base_url}/?reserved=5000&balance=1000")
            time.sleep(2)
            
            balance_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '1000') or contains(text(), '1') and contains(text(), '000')]")
            reserved_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '5000') or contains(text(), '5') and contains(text(), '000')]")
            
            self.assertTrue(len(balance_elements) > 0 and len(reserved_elements) > 0)
            
        except Exception as e:
            self.fail(f"URL parameters validation test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 