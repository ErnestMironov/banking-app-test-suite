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
        # Закрываем alert если он есть (от предыдущих тестов)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except:
            pass
    
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
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()

            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")

            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            self.assertTrue(amount_input.is_displayed())

        except Exception as e:
            self.fail(f"Card number validation test failed: {str(e)}")
    
    def test_03_card_number_validation_incorrect(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("12345")
            
            time.sleep(1)
            
            amount_inputs = self.driver.find_elements(By.XPATH, "//input[@placeholder='1000']")
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'ошибка') or contains(text(), 'неверн') or contains(@class, 'error')]")
            
            self.assertTrue(len(amount_inputs) == 0 or len(error_elements) > 0)
            
        except Exception as e:
            self.fail(f"Incorrect card number validation test failed: {str(e)}")
    
    def test_04_successful_transfer_with_commission(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            amount_input.clear()
            amount_input.send_keys("1000")
            
            time.sleep(1)
            
            commission_element = self.driver.find_element(By.XPATH, "//*[@id='comission' or contains(text(), '100')]")
            self.assertTrue(commission_element.is_displayed())
            
            transfer_button = self.driver.find_element(By.XPATH, "//button[.//span[text()='Перевести']]")
            self.assertTrue(transfer_button.is_displayed())
            
            transfer_button.click()
            
            # Ожидаем и проверяем alert об успешном переводе
            time.sleep(1)
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.assertIn("принят банком", alert_text)
                alert.accept()
            except:
                self.fail("Expected success alert after transfer")
            
        except Exception as e:
            self.fail(f"Successful transfer test failed: {str(e)}")
    
    def test_05_transfer_exceeds_available_amount(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.clear()
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            amount_input.clear()
            amount_input.send_keys("15000")
            
            time.sleep(2)
            
            error_messages = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Недостаточно средств')]")
            transfer_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Перевести')]")
            
            self.assertTrue(len(error_messages) > 0 or len(transfer_buttons) == 0)
            
        except Exception as e:
            self.fail(f"Transfer exceeds amount test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 