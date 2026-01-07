# 🚀 KURULUM VE ÇALIŞTIRMA REHBERİ

## ADIM 1: Python'u Yükleyin

Eğer Python yüklü değilse:

1. https://www.python.org/downloads/ adresine gidin
2. "Download Python" butonuna tıklayın
3. İndirilen dosyayı çalıştırın
4. **ÖNEMLİ:** Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin!
5. Kurulumu tamamlayın

Kurulumdan sonra bilgisayarınızı yeniden başlatın.

## ADIM 2: Python'un Yüklü Olduğunu Kontrol Edin

PowerShell veya CMD'yi açın ve şu komutu çalıştırın:

```bash
python --version
```

Eğer Python sürümü görünüyorsa (örn: Python 3.11.5), devam edin.

## ADIM 3: Gerekli Paketleri Yükleyin

Proje klasörüne gidin ve şu komutu çalıştırın:

```bash
cd C:\Users\Kayra\Desktop\Ai
pip install -r requirements.txt
```

## ADIM 4: OpenAI API Anahtarı Ayarlayın

1. `.env` dosyası oluşturun (proje klasöründe)
2. İçine şunu yazın:

```
OPENAI_API_KEY=your_api_key_here
```

API anahtarınızı [buradan](https://platform.openai.com/api-keys) alabilirsiniz.

## ADIM 5: Programı Çalıştırın

PowerShell veya CMD'de:

```bash
cd C:\Users\Kayra\Desktop\Ai
python main.py
```

## HIZLI BAŞLATMA (Windows için)

Aşağıdaki `BASLA.bat` dosyasını çift tıklayarak da başlatabilirsiniz!

