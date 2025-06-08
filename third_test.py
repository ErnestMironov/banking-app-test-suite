import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class BankServiceUITests(unittest.TestCase):
    
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
    
    def test_11_responsive_design_mobile_simulation(self):
        try:
            # Эмуляция мобильного устройства
            self.driver.set_window_size(375, 667)  # iPhone SE размер
            time.sleep(2)
            
            # Проверяем что элементы отображаются корректно
            title_element = self.driver.find_element(By.XPATH, "//h1[text()='F-Bank']")
            self.assertTrue(title_element.is_displayed())
            
            # Проверяем карточки счетов
            rub_card = self.driver.find_element(By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]")
            self.assertTrue(rub_card.is_displayed())
            
            # Возвращаем обычный размер
            self.driver.set_window_size(1280, 720)
            time.sleep(1)
            
        except Exception as e:
            self.fail(f"Responsive design test failed: {str(e)}")
    
    def test_12_performance_load_time(self):
        try:
            start_time = time.time()
            
            self.driver.get(f"{self.base_url}/?balance=50000&reserved=10000")
            
            # Ждем полной загрузки страницы
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//h1[text()='F-Bank']"))
            )
            
            load_time = time.time() - start_time
            
            # Проверяем что страница загрузилась за разумное время
            self.assertLess(load_time, 5.0, "Page should load within 5 seconds")
            
            # Проверяем что все основные элементы присутствуют
            balance_element = self.driver.find_element(By.XPATH, "//span[@id='rub-sum']")
            self.assertEqual(balance_element.text, "50'000")
            
        except Exception as e:
            self.fail(f"Performance test failed: {str(e)}")
    
    def test_13_multiple_clicks_rapid_input(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            
            # Множественные быстрые клики
            for i in range(5):
                rub_button.click()
                time.sleep(0.1)
            
            # Проверяем что интерфейс остался стабильным
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            
            # Быстрый ввод данных
            for char in "1234567890123456":
                card_input.send_keys(char)
                time.sleep(0.05)
            
            # Проверяем корректность введенных данных
            card_value = card_input.get_attribute("value")
            self.assertIn("1234", card_value)
            
            # Проверяем что поле суммы появилось
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            self.assertTrue(amount_input.is_displayed())
            
        except Exception as e:
            self.fail(f"Multiple clicks rapid input test failed: {str(e)}")
    
    def test_14_bug_005_zero_amount_transfer_allowed(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            
            # Вводим нулевую сумму
            amount_input.send_keys("0")
            time.sleep(2)
            
            # Проверяем что кнопка НЕ должна быть активна для нулевой суммы
            transfer_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Перевести')]")
            
            if len(transfer_buttons) > 0:
                button = transfer_buttons[0]
                self.assertFalse(button.is_enabled(), "Transfer button should be disabled for zero amount")
            else:
                self.fail("Transfer button should exist but be disabled for zero amount")
            
        except Exception as e:
            self.fail(f"Zero amount transfer test failed: {str(e)}")
    
    def test_15_bug_006_decimal_amount_processing(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            card_input.send_keys("1234567890123456")
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            
            # Вводим дробную сумму
            amount_input.send_keys("100.50")
            time.sleep(2)
            
            # Проверяем отображаемую сумму - должна быть 100.50, но система показывает 10050
            displayed_amount = amount_input.get_attribute("value")
            
            # Ожидаем корректную обработку как 100.50, но получаем 10050 (это баг)
            self.assertEqual(displayed_amount, "100.50", f"Decimal amount should be processed as 100.50, but got: {displayed_amount}")
            
            # Проверяем комиссию - должна быть от 100.50, а не от 10050
            commission_element = self.driver.find_element(By.XPATH, "//span[@id='comission']")
            commission_text = commission_element.text
            
            # Ожидаем комиссию ~10, но получаем от 10050 (это баг)
            self.assertTrue("10" in commission_text and "1005" not in commission_text, 
                          f"Commission should be calculated from 100.50, not 10050. Got: {commission_text}")
            
        except Exception as e:
            self.fail(f"Decimal amount processing test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 