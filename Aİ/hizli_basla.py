"""
Hızlı başlatma scripti - Varsayılan değerlerle çalıştırır
"""
import sys
from main import main

# Varsayılan değerler
DEFAULT_BOOK_URL = "https://aydinlikyarinlara.com/zkitap/peygamberime-inaniyorum/"
DEFAULT_QUIZ_URL = ""  # Yarışma URL'sini buraya ekleyin

def quick_start():
    print("=" * 50)
    print("HIZLI BAŞLATMA MODU")
    print("=" * 50)
    print("\nVarsayılan değerler:")
    print(f"📚 Kitap: {DEFAULT_BOOK_URL}")
    
    if DEFAULT_QUIZ_URL:
        print(f"🏆 Yarışma: {DEFAULT_QUIZ_URL}")
        use_defaults = input("\nVarsayılan değerleri kullanmak istiyor musunuz? (e/h): ").strip().lower()
        
        if use_defaults == 'e':
            # Varsayılan değerlerle çalıştır
            import io
            from contextlib import redirect_stdout
            
            # Input'ları simüle et
            class InputSimulator:
                def __init__(self, inputs):
                    self.inputs = inputs
                    self.index = 0
                
                def __call__(self, prompt=''):
                    if self.index < len(self.inputs):
                        value = self.inputs[self.index]
                        self.index += 1
                        print(prompt + value)
                        return value
                    return input(prompt)
            
            # Input fonksiyonunu geçici olarak değiştir
            original_input = __builtins__['input']
            __builtins__['input'] = InputSimulator([DEFAULT_BOOK_URL, DEFAULT_QUIZ_URL])
            
            try:
                main()
            finally:
                __builtins__['input'] = original_input
            return
    
    # Normal mod
    print("\nManuel giriş modu:")
    main()

if __name__ == "__main__":
    quick_start()

