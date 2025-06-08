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
    
    def test_14_keyboard_accessibility(self):
        try:
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            
            # Проверяем доступность с клавиатуры
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.TAB).perform()  # Переход к первому элементу
            time.sleep(0.5)
            
            # Нажимаем Enter на карточке
            rub_button.click()  # Симуляция клика с клавиатуры
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            
            # Проверяем что можем вводить с клавиатуры
            card_input.send_keys("1234567890123456")
            
            # Используем Tab для перехода к следующему полю
            card_input.send_keys(Keys.TAB)
            
            amount_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1000']"))
            )
            
            # Вводим сумму
            amount_input.send_keys("2000")
            time.sleep(1)
            
            # Проверяем что все поля доступны для навигации
            self.assertTrue(card_input.is_enabled())
            self.assertTrue(amount_input.is_enabled())
            
        except Exception as e:
            self.fail(f"Keyboard accessibility test failed: {str(e)}")
    
    def test_15_data_security_no_persistence(self):
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
            amount_input.send_keys("5000")
            
            # Обновляем страницу
            self.driver.refresh()
            time.sleep(2)
            
            # Проверяем что данные не сохранились
            rub_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'g-card') and .//h2[text()='Рубли']]"))
            )
            rub_button.click()
            
            card_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0000 0000 0000 0000']"))
            )
            
            # Поле должно быть пустым
            card_value = card_input.get_attribute("value")
            self.assertEqual(card_value, "", "Card input should be empty after page refresh")
            
            # Проверяем что в локальном хранилище нет чувствительных данных
            local_storage_keys = self.driver.execute_script("return Object.keys(localStorage);")
            session_storage_keys = self.driver.execute_script("return Object.keys(sessionStorage);")
            
            # Не должно быть ключей связанных с картами
            card_related_keys = [key for key in local_storage_keys + session_storage_keys 
                               if 'card' in key.lower() or 'credit' in key.lower()]
            self.assertEqual(len(card_related_keys), 0, "No card-related data should be stored")
            
        except Exception as e:
            self.fail(f"Data security test failed: {str(e)}")


if __name__ == "__main__":
    unittest.main() 