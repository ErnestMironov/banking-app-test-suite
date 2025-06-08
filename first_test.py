import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class BankServiceTests(unittest.TestCase):
    
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
    
    def setUp(self):
        self.driver.get(f"{self.base_url}/?balance=30000&reserved=20001")
        time.sleep(2)
    
    def test_01_balance_display(self):
        try:
            balance_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '30') and contains(text(), '000')]"))
            )
            self.assertTrue(balance_element.is_displayed())
            
            reserved_element = self.driver.find_element(By.XPATH, "//*[contains(text(), '20') and contains(text(), '001')]")
            self.assertTrue(reserved_element.is_displayed())
            
        except Exception as e:
            self.fail(f"Balance display test failed: {str(e)}")
    
    def test_02_card_number_validation_correct(self):
        try:
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
            self.assertTrue(amount_input.is_displayed())
            
        except Exception as e:
            self.fail(f"Card number validation test failed: {str(e)}")
    
    def test_03_card_number_validation_incorrect(self):
        try:
            account_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'account') or contains(text(), 'руб')]"))
            )
            account_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @placeholder]"))
            )
            card_input.clear()
            card_input.send_keys("12345")
            
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Подтвердить') or contains(text(), 'Далее')]")
            confirm_button.click()
            
            time.sleep(1)
            
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'ошибка') or contains(text(), 'неверн') or contains(@class, 'error')]")
            amount_inputs = self.driver.find_elements(By.XPATH, "//input[@type='number']")
            
            self.assertTrue(len(error_elements) > 0 or len(amount_inputs) == 0)
            
        except Exception as e:
            self.fail(f"Incorrect card number validation test failed: {str(e)}")
    
    def test_04_successful_transfer_with_commission(self):
        try:
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
            amount_input.send_keys("5000")
            
            time.sleep(1)
            
            commission_element = self.driver.find_element(By.XPATH, "//*[contains(text(), '500') or contains(text(), 'комиссия')]")
            self.assertTrue(commission_element.is_displayed())
            
            transfer_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Перевести')]")
            self.assertTrue(transfer_button.is_displayed())
            
            transfer_button.click()
            
            notification = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'принял') or contains(text(), 'запрос')]"))
            )
            self.assertTrue(notification.is_displayed())
            
        except Exception as e:
            self.fail(f"Successful transfer test failed: {str(e)}")
    
    def test_05_transfer_exceeds_available_amount(self):
        try:
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
            amount_input.send_keys("9500")
            
            time.sleep(2)
            
            error_messages = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'невозможен') or contains(text(), 'недостаточно')]")
            transfer_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Перевести')]")
            
            self.assertTrue(len(error_messages) > 0 or len(transfer_buttons) == 0)
            
        except Exception as e:
            self.fail(f"Transfer exceeds amount test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 