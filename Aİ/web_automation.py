"""
Web otomasyon modülü - Selenium ile siteye gidip form doldurma
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from typing import List, Dict


class WebAutomation:
    def __init__(self, headless: bool = False):
        """
        Args:
            headless: Tarayıcıyı görünmez modda çalıştır (varsayılan: False)
        """
        self.driver = None
        self.headless = headless
        
    def start_browser(self):
        """Tarayıcıyı başlatır"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            print("🔧 ChromeDriver yükleniyor...")
            service = Service(ChromeDriverManager().install())
            print("🌐 Tarayıcı başlatılıyor...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.maximize_window()
            print("✅ Tarayıcı hazır")
        except Exception as e:
            print(f"❌ Tarayıcı başlatılırken hata: {e}")
            raise
        
    def navigate_to(self, url: str):
        """Belirtilen URL'ye gider"""
        if not self.driver:
            self.start_browser()
        
        # URL formatını kontrol et
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            print(f"🌐 {url} adresine gidiliyor...")
            self.driver.get(url)
            time.sleep(3)  # Sayfanın yüklenmesi için bekle
            print("✅ Sayfa yüklendi")
        except Exception as e:
            print(f"❌ Sayfa yüklenirken hata: {e}")
            raise
    
    def find_questions(self) -> List[Dict[str, str]]:
        """
        Sayfadaki soruları bulur
        
        Returns:
            Soru listesi [{"question": "...", "element": selenium_element}, ...]
        """
        questions = []
        
        # Farklı soru formatlarını dene
        # Input alanları, textarea'lar, soru metinleri vb.
        try:
            # Soru metinlerini bul (genellikle label, p, div, span içinde)
            question_elements = self.driver.find_elements(By.XPATH, 
                "//label | //p[contains(@class, 'question')] | //div[contains(@class, 'question')] | //span[contains(@class, 'question')]")
            
            for elem in question_elements:
                text = elem.text.strip()
                if text and len(text) > 10:  # En az 10 karakterlik metin
                    questions.append({
                        "question": text,
                        "element": elem
                    })
        except Exception as e:
            print(f"Sorular bulunurken hata: {e}")
        
        return questions
    
    def find_answer_inputs(self) -> List[object]:
        """Sayfadaki cevap input alanlarını bulur"""
        inputs = []
        try:
            # Text input, textarea, select vb. bul
            input_elements = self.driver.find_elements(By.XPATH,
                "//input[@type='text'] | //textarea | //input[@type='textarea'] | //select")
            inputs.extend(input_elements)
        except Exception as e:
            print(f"Input alanları bulunurken hata: {e}")
        
        return inputs
    
    def fill_answer(self, input_element, answer: str):
        """Cevap alanına cevabı yazar"""
        try:
            input_element.clear()
            input_element.send_keys(answer)
            time.sleep(0.5)
        except Exception as e:
            print(f"Cevap yazılırken hata: {e}")
    
    def submit_form(self):
        """Formu gönderir"""
        try:
            # Submit butonunu bul
            submit_button = self.driver.find_element(By.XPATH,
                "//button[@type='submit'] | //input[@type='submit'] | //button[contains(text(), 'Gönder')] | //button[contains(text(), 'Submit')]")
            submit_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Form gönderilirken hata: {e}")
    
    def get_page_source(self) -> str:
        """Sayfa kaynağını döndürür"""
        return self.driver.page_source
    
    def close(self):
        """Tarayıcıyı kapatır"""
        if self.driver:
            self.driver.quit()
            self.driver = None

