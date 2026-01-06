from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import Optional

class BrowserController:
    def __init__(self, headless: bool = False):
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
        self.wait_timeout = 10
    
    def start_browser(self) -> bool:
        """Initialize Chrome browser."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.maximize_window()
            return True
        except Exception as e:
            print(f"Browser start error: {e}")
            return False
    
    def navigate(self, url: str) -> bool:
        """Navigate to URL."""
        try:
            if not self.driver:
                self.start_browser()
            
            if not url.startswith("http"):
                url = f"https://{url}"
            
            self.driver.get(url)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Navigation error: {e}")
            return False
    
    def search_youtube(self, query: str) -> bool:
        """Search and play video on YouTube."""
        try:
            # Navigate to YouTube
            self.navigate("https://www.youtube.com")
            time.sleep(2)
            
            # Find search box
            search_box = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            # Click first video
            first_video = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
            )
            first_video.click()
            
            time.sleep(2)
            return True
        except Exception as e:
            print(f"YouTube search error: {e}")
            return False
    
    def search_google(self, query: str) -> bool:
        """Search on Google."""
        try:
            self.navigate("https://www.google.com")
            time.sleep(2)
            
            search_box = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Google search error: {e}")
            return False
    
    def fill_form(self, field_selector: str, value: str) -> bool:
        """Fill form field."""
        try:
            field = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, field_selector))
            )
            field.clear()
            field.send_keys(value)
            return True
        except Exception as e:
            print(f"Form fill error: {e}")
            return False
    
    def click_element(self, selector: str) -> bool:
        """Click element."""
        try:
            element = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def close_browser(self):
        """Close browser."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            print(f"Browser close error: {e}")
