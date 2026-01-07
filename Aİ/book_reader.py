"""
Kitap okuma modülü - PDF, TXT dosyalarını ve web sitelerinden kitap okur
"""
import PyPDF2
import os
import re
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


class BookReader:
    def __init__(self, book_path: str):
        """
        Args:
            book_path: Kitap dosyasının yolu (PDF, TXT) veya web sitesi URL'si
        """
        self.book_path = book_path
        self.content = None
        
    def read(self) -> str:
        """Kitabı okur ve içeriği döndürür"""
        # URL kontrolü
        if self.book_path.startswith(('http://', 'https://')):
            return self._read_web()
        
        # Dosya kontrolü
        if not os.path.exists(self.book_path):
            raise FileNotFoundError(f"Kitap dosyası bulunamadı: {self.book_path}")
        
        file_ext = os.path.splitext(self.book_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._read_pdf()
        elif file_ext == '.txt':
            return self._read_txt()
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}")
    
    def _read_web(self) -> str:
        """Web sitesinden kitabı okur (aydinlikyarinlara.com için özel)"""
        print("🌐 Web sitesinden kitap okunuyor...")
        driver = None
        try:
            # Chrome tarayıcısını başlat
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.maximize_window()
            
            # Base URL'i al (#p=10 gibi kısımları kaldır)
            base_url = self.book_path.split('#')[0]
            if not base_url.endswith('/'):
                base_url += '/'
            
            # İlk sayfaya git
            first_page_url = base_url + "#p=1"
            driver.get(first_page_url)
            time.sleep(4)  # Sayfa yüklenmesi için bekle
            
            all_text = ""
            page_num = 1
            max_pages = 1000  # Maksimum sayfa sayısı
            consecutive_errors = 0
            last_content = ""
            
            print("📖 Sayfalar okunuyor...")
            
            while page_num <= max_pages:
                try:
                    # Sayfa içeriğini bul
                    page_content = ""
                    
                    # Önce sayfa yüklenmesini bekle
                    time.sleep(2)
                    
                    # aydinlikyarinlara.com için özel selector'lar
                    selectors = [
                        "div.zkitap-content",
                        "div.zkitap-page",
                        "div.book-page",
                        "div.page-text",
                        "div[class*='zkitap']",
                        "div[class*='book']",
                        "div[class*='page']",
                        "article",
                        "main",
                        "div.content"
                    ]
                    
                    found_content = False
                    for selector in selectors:
                        try:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            for elem in elements:
                                text = elem.text.strip()
                                # Navigasyon ve menü metinlerini filtrele
                                if text and len(text) > 100 and not any(skip in text.lower() for skip in ['menü', 'menu', 'giriş', 'kayıt', 'login', 'register']):
                                    page_content += text + "\n"
                                    found_content = True
                        except:
                            continue
                    
                    # Eğer özel selector'lar çalışmazsa, body'den metni al ama filtrele
                    if not found_content or len(page_content) < 100:
                        try:
                            body = driver.find_element(By.TAG_NAME, "body")
                            full_text = body.text
                            # Gereksiz kısımları temizle
                            lines = full_text.split('\n')
                            filtered_lines = []
                            for line in lines:
                                line = line.strip()
                                if len(line) > 20 and not any(skip in line.lower() for skip in ['menü', 'menu', 'giriş', 'kayıt', 'anasayfa', 'home', 'copyright']):
                                    filtered_lines.append(line)
                            page_content = '\n'.join(filtered_lines)
                        except:
                            pass
                    
                    # İçerik kontrolü
                    if page_content and len(page_content) > 100:
                        # Aynı içerik tekrar ediyorsa dur
                        if page_content == last_content and page_num > 3:
                            print(f"📄 Son sayfaya ulaşıldı (Sayfa {page_num-1})")
                            break
                        
                        all_text += f"\n--- Sayfa {page_num} ---\n"
                        all_text += page_content + "\n"
                        last_content = page_content
                        print(f"✅ Sayfa {page_num} okundu ({len(page_content)} karakter)")
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                        if consecutive_errors >= 3:
                            print(f"📄 {consecutive_errors} ardışık sayfa boş, son sayfaya ulaşıldı")
                            break
                    
                    # Sonraki sayfaya geç
                    next_page_url = base_url + f"#p={page_num + 1}"
                    driver.get(next_page_url)
                    time.sleep(3)  # Sayfa yüklenmesi için bekle
                    
                    page_num += 1
                    
                    # Her 20 sayfada bir ilerleme göster
                    if page_num % 20 == 0:
                        print(f"📊 {page_num-1} sayfa okundu, devam ediliyor...")
                    
                except Exception as e:
                    consecutive_errors += 1
                    print(f"⚠️  Sayfa {page_num} okunurken hata: {str(e)[:50]}")
                    if consecutive_errors >= 3:
                        print(f"📄 {consecutive_errors} ardışık hata, okuma durduruluyor")
                        break
                    page_num += 1
                    if page_num <= max_pages:
                        try:
                            next_url = base_url + f"#p={page_num}"
                            driver.get(next_url)
                            time.sleep(2)
                        except:
                            break
                    continue
            
            if not all_text or len(all_text) < 500:
                raise Exception("Kitap içeriği yeterli değil veya bulunamadı. Site yapısı farklı olabilir.")
            
            self.content = all_text
            total_pages = page_num - 1
            print(f"\n✅ Toplam {total_pages} sayfa okundu! ({len(all_text)} karakter)")
            return all_text
            
        except Exception as e:
            raise Exception(f"Web sitesinden kitap okunurken hata: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _read_pdf(self) -> str:
        """PDF dosyasını okur"""
        text = ""
        with open(self.book_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        self.content = text
        return text
    
    def _read_txt(self) -> str:
        """TXT dosyasını okur"""
        with open(self.book_path, 'r', encoding='utf-8') as file:
            text = file.read()
        self.content = text
        return text
    
    def get_content(self) -> Optional[str]:
        """Okunan içeriği döndürür"""
        return self.content

