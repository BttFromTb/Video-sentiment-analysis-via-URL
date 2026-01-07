# Kitap Yarışması Otomasyonu 🤖📚

Bu proje, bir kitap yarışmasında otomatik olarak soruları çözmek için tasarlanmış bir yapay zeka otomasyonudur.

## Özellikler

- 📖 PDF ve TXT formatındaki kitapları okur
- 🤖 OpenAI API kullanarak soruları kitaba göre cevaplar
- 🌐 Selenium ile web sitesine otomatik giriş yapar
- 📝 Soruları bulur ve cevapları otomatik doldurur

## Kurulum

### 1. Gereksinimleri yükleyin

```bash
pip install -r requirements.txt
```

### 2. Chrome tarayıcısını yükleyin

Chrome tarayıcısının sisteminizde yüklü olması gerekir. ChromeDriver otomatik olarak yüklenecektir.

### 3. OpenAI API anahtarını ayarlayın

`.env` dosyası oluşturun ve API anahtarınızı ekleyin:

```bash
OPENAI_API_KEY=your_api_key_here
```

API anahtarınızı [OpenAI Platform](https://platform.openai.com/api-keys) adresinden alabilirsiniz.

## Kullanım

1. Kitap dosyanızı proje klasörüne koyun (PDF veya TXT formatında)

2. Programı çalıştırın:

```bash
python main.py
```

3. Program sizden şunları isteyecek:
   - Kitap dosyasının yolunu
   - Yarışma sitesinin URL'sini

4. Program otomatik olarak:
   - Kitabı okuyacak
   - Siteye gidecek
   - Soruları bulacak
   - AI ile cevapları üretecek
   - Formu dolduracak

## Notlar

- ⚠️ Bu araç eğitim amaçlıdır. Yarışma kurallarını kontrol edin.
- 🔍 Bazı siteler için soru bulma algoritmasını özelleştirmeniz gerekebilir.
- 💰 OpenAI API kullanımı ücretlidir. Kullanımınızı kontrol edin.
- 🌐 İnternet bağlantısı gereklidir.

## Sorun Giderme

### ChromeDriver hatası
Chrome tarayıcısının güncel olduğundan emin olun. webdriver-manager otomatik olarak uygun sürücüyü yükleyecektir.

### API anahtarı hatası
`.env` dosyasının doğru konumda olduğundan ve API anahtarının doğru girildiğinden emin olun.

### Soru bulunamıyor
Farklı web siteleri farklı HTML yapıları kullanır. `web_automation.py` dosyasındaki `find_questions()` metodunu siteye göre özelleştirmeniz gerekebilir.

## Lisans

Bu proje eğitim amaçlıdır.

