"""
Ana script - Kitap yarışması otomasyonu
"""
import os
import sys
import traceback
from selenium.webdriver.common.by import By
from book_reader import BookReader
from ai_solver import AISolver
from web_automation import WebAutomation
import time


def main():
    print("=" * 50)
    print("KİTAP YARIŞMASI OTOMASYONU")
    print("=" * 50)
    
    # Kullanıcıdan bilgileri al
    print("\n📚 Kitap bilgisi:")
    print("   - Web sitesi URL'si (örn: https://aydinlikyarinlara.com/zkitap/...)")
    print("   - Veya dosya yolu (PDF veya TXT)")
    book_path = input("\nKitap URL'si veya dosya yolunu girin: ").strip()
    if not book_path:
        print("Hata: Kitap yolu/URL girilmedi!")
        return
    
    url = input("\nYarışma sitesinin URL'sini girin: ").strip()
    if not url:
        print("Hata: Yarışma URL'si girilmedi!")
        return
    
    # Kitabı oku
    print("\n📖 Kitap okunuyor...")
    try:
        reader = BookReader(book_path)
        book_content = reader.read()
        print(f"✅ Kitap okundu! ({len(book_content)} karakter)")
    except Exception as e:
        print(f"❌ Kitap okunurken hata: {e}")
        return
    
    # AI solver'ı başlat
    print("\n🤖 AI çözücü hazırlanıyor...")
    try:
        solver = AISolver()
        solver.set_book_content(book_content)
        print("✅ AI çözücü hazır!")
    except Exception as e:
        print(f"❌ AI çözücü başlatılırken hata: {e}")
        print("💡 .env dosyasına OPENAI_API_KEY eklediğinizden emin olun!")
        return
    
    # Web otomasyonunu başlat
    print("\n🌐 Web otomasyonu başlatılıyor...")
    automation = WebAutomation(headless=False)  # Tarayıcıyı görmek için False
    
    try:
        automation.start_browser()
        print(f"✅ Tarayıcı açıldı, {url} adresine gidiliyor...")
        automation.navigate_to(url)
        
        # Kullanıcıya sayfanın yüklendiğini bildir
        input("\n⏸️  Sayfa yüklendi. Sayfayı kontrol edin ve Enter'a basın...")
        
        # Soruları bul
        print("\n🔍 Sorular aranıyor...")
        questions = automation.find_questions()
        answer_inputs = automation.find_answer_inputs()
        
        print(f"✅ {len(questions)} soru bulundu")
        print(f"✅ {len(answer_inputs)} cevap alanı bulundu")
        
        if not answer_inputs:
            print("⚠️  Cevap alanları bulunamadı. Sayfayı kontrol edin.")
            input("Enter'a basın...")
            automation.close()
            return
        
        # Her soruyu çöz ve cevapla
        print("\n📝 Sorular çözülüyor...")
        for i, input_elem in enumerate(answer_inputs):
            try:
                # Sayfadaki soru metnini bulmaya çalış
                question_text = f"Soru {i+1}"
                
                # Input'un yakınındaki soru metnini bul
                try:
                    parent = input_elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'question') or contains(@class, 'form-group')][1]")
                    question_elem = parent.find_element(By.XPATH, ".//label | .//p | .//div | .//span")
                    question_text = question_elem.text.strip()
                except:
                    pass
                
                print(f"\n❓ Soru {i+1}: {question_text[:100]}...")
                
                # AI ile cevabı bul
                answer = solver.solve_question(question_text)
                print(f"✅ Cevap: {answer[:100]}...")
                
                # Cevabı yaz
                automation.fill_answer(input_elem, answer)
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️  Soru {i+1} çözülürken hata: {e}")
                continue
        
        # Formu gönderme seçeneği
        submit = input("\n\n📤 Formu göndermek istiyor musunuz? (e/h): ").strip().lower()
        if submit == 'e':
            automation.submit_form()
            print("✅ Form gönderildi!")
        else:
            print("⏸️  Form gönderilmedi. Manuel kontrol edebilirsiniz.")
        
        input("\n⏸️  İşlem tamamlandı. Enter'a basarak tarayıcıyı kapatın...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata oluştu: {e}")
        print("\n🔍 Detaylı hata bilgisi:")
        traceback.print_exc()
        input("\n⏸️  Hata detaylarını görmek için yukarıdaki bilgileri kontrol edin. Enter'a basın...")
    finally:
        try:
            automation.close()
            print("\n✅ Tarayıcı kapatıldı.")
        except:
            pass
        print("İyi şanslar! 🍀")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        traceback.print_exc()
        input("\n⏸️  Enter'a basarak çıkın...")

