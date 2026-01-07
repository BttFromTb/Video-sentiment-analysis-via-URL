# 🎥 YouTube Video Duygu Analizi

Bu program, YouTube video URL'si alır, videodaki konuşmayı metne dönüştürür ve ruh halini/duyguyu analiz eder.

## Özellikler

- 📺 YouTube video URL'sinden otomatik transkript alır
- 🎤 Otomatik alt yazıları (captions) kullanır
- 😊 Duygu analizi yapar (Mutlu, Üzgün, Kızgın, Nötr, vb.)
- 🤖 OpenAI ile gelişmiş analiz (opsiyonel)
- 📊 Pozitiflik oranı ve subjektivite skoru

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. (Opsiyonel) OpenAI API anahtarı için `.env` dosyası oluşturun:
```
OPENAI_API_KEY=your_api_key_here
```

## Kullanım

### Basit Kullanım

```bash
python video_duygu_analizi.py
```

Program sizden:
1. YouTube video URL'sini isteyecek
2. AI analizi yapmak isteyip istemediğinizi soracak
3. Sonuçları gösterecek

### Örnek

```
📺 YouTube video URL'sini girin: https://youtube.com/shorts/lMgzjc23Lh0

🤖 AI ile detaylı analiz yapmak istiyor musunuz? (e/h): e

📊 ANALİZ SONUÇLARI
😊 Ruh Hali: Mutlu 😊
📈 Duygu: Pozitif
📊 Pozitiflik Oranı: %75.5
```

## Nasıl Çalışır?

1. **Transkript Alma**: yt-dlp kullanarak YouTube'dan otomatik alt yazıları alır
2. **Metin Analizi**: TextBlob ile duygu analizi yapar
3. **AI Analizi** (opsiyonel): OpenAI GPT ile daha detaylı analiz yapar

## Desteklenen Formatlar

- YouTube video URL'leri
- YouTube Shorts URL'leri
- Otomatik alt yazılar (captions)
- Manuel alt yazılar

## Notlar

- ⚠️ Video transkripti olmayan videolarda analiz yapılamaz
- 💰 OpenAI API kullanımı ücretlidir
- 🌐 İnternet bağlantısı gereklidir

## Sorun Giderme

### "Transkript bulunamadı" hatası
Video otomatik alt yazıya sahip değilse analiz yapılamaz. Başka bir video deneyin.

### TextBlob Türkçe desteği
TextBlob Türkçe için ek veri gerektirebilir. İngilizce videolarda daha iyi çalışır.

