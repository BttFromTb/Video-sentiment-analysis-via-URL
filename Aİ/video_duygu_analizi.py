"""
YouTube Video Duygu Analizi
URL'den videoyu alır, metne dönüştürür ve ruh halini analiz eder
"""
import os
import sys
from typing import Dict, Optional
import re
import json

# Paketleri kontrol et ve yükle
missing_packages = []

try:
    from yt_dlp import YoutubeDL
except ImportError:
    missing_packages.append("yt-dlp")

try:
    from openai import OpenAI
except ImportError:
    missing_packages.append("openai")

try:
    from textblob import TextBlob
except ImportError:
    missing_packages.append("textblob")

try:
    from dotenv import load_dotenv
except ImportError:
    missing_packages.append("python-dotenv")

if missing_packages:
    print("❌ Gerekli paketler yüklü değil!")
    print(f"Eksik paketler: {', '.join(missing_packages)}")
    print("Lütfen şu komutu çalıştırın: pip install -r requirements.txt")
    input("Enter'a basın...")
    sys.exit(1)

# Import'ları yap
from yt_dlp import YoutubeDL
from openai import OpenAI
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()


class VideoDuyguAnalizi:
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API anahtarı (opsiyonel, .env'den de alınabilir)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
    
    def get_video_transcript(self, url: str) -> str:
        """
        YouTube videosundan transkripti alır
        
        Args:
            url: YouTube video URL'si
            
        Returns:
            Video transkripti (metin)
        """
        print("🎥 Video analiz ediliyor...")
        
        try:
            # yt-dlp ile video bilgilerini al
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['tr', 'en'],  # Önce tr ve en, sonra tüm dilleri manuel kontrol edeceğiz
                'skip_download': True,
                'quiet': True,  # Sessiz mod
                'no_warnings': False,
                'extract_flat': False,
                'ignoreerrors': False,  # Hataları göster
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                print("📝 Video bilgileri alınıyor...")
                info = None
                error_occurred = False
                
                try:
                    # İlk deneme - normal mod
                    info = ydl.extract_info(url, download=False)
                except Exception as e:
                    error_msg = str(e)
                    error_occurred = True
                    print(f"⚠️  İlk deneme başarısız: {error_msg[:150]}")
                    
                    # Özel hata mesajları
                    if 'Private video' in error_msg or 'private' in error_msg.lower():
                        raise Exception("Bu video özel (private). Transkript alınamaz.")
                    elif 'Video unavailable' in error_msg or 'unavailable' in error_msg.lower():
                        raise Exception("Video mevcut değil veya silinmiş.")
                    elif 'Sign in' in error_msg or 'age-restricted' in error_msg.lower():
                        raise Exception("Video yaş kısıtlamalı veya giriş gerektiriyor.")
                    
                    # Alternatif yöntem dene
                    try:
                        print("🔄 Alternatif yöntem deneniyor...")
                        ydl_opts_alt = ydl_opts.copy()
                        ydl_opts_alt['quiet'] = True
                        ydl_opts_alt['no_warnings'] = True
                        with YoutubeDL(ydl_opts_alt) as ydl_alt:
                            info = ydl_alt.extract_info(url, download=False)
                    except Exception as e2:
                        print(f"❌ Alternatif yöntem de başarısız: {str(e2)[:150]}")
                        raise Exception(f"Video bilgileri alınamadı. Hata: {error_msg[:200]}")
                
                if not info:
                    if error_occurred:
                        raise Exception("Video bilgileri alınamadı. Video erişilebilir mi kontrol edin.")
                    else:
                        raise Exception("Video bilgileri alınamadı (info None). Video URL'si doğru mu kontrol edin.")
                
                # Tüm mevcut alt yazıları kontrol et
                subtitles = info.get('subtitles', {}) if info else {}
                auto_captions = info.get('automatic_captions', {}) if info else {}
                
                print(f"🔍 Mevcut alt yazılar: {list(subtitles.keys()) if subtitles else 'Yok'}")
                print(f"🔍 Otomatik alt yazılar: {list(auto_captions.keys()) if auto_captions else 'Yok'}")
                
                transcript_text = ""
                
                # Tüm dilleri topla
                all_languages = set()
                if subtitles:
                    all_languages.update(subtitles.keys())
                if auto_captions:
                    all_languages.update(auto_captions.keys())
                
                # Öncelik sırası: tr, en, diğer diller
                languages_to_try = ['tr', 'en'] + [lang for lang in all_languages if lang not in ['tr', 'en']]
                
                print(f"🌐 Denenecek diller: {languages_to_try[:5]}...")  # İlk 5'ini göster
                
                for lang in languages_to_try:
                    if not transcript_text:
                        # Önce manuel alt yazıları dene
                        if lang in subtitles:
                            print(f"📝 {lang} manuel alt yazı deneniyor...")
                            transcript_text = self._download_subtitle(url, lang, auto=False)
                            if transcript_text and len(transcript_text) > 50:
                                break
                        
                        # Sonra otomatik alt yazıları dene
                        if not transcript_text and lang in auto_captions:
                            print(f"📝 {lang} otomatik alt yazı deneniyor...")
                            transcript_text = self._download_subtitle(url, lang, auto=True)
                            if transcript_text and len(transcript_text) > 50:
                                break
                
                if transcript_text and len(transcript_text) > 50:
                    print(f"✅ Transkript alındı! ({len(transcript_text)} karakter)")
                    return transcript_text
                
                # Eğer transkript yoksa, video başlığı ve açıklamasını kullan
                print("\n⚠️  Transkript bulunamadı!")
                title = info.get('title', '')
                description = info.get('description', '')
                
                # Açıklamayı temizle (linkler, hashtag'ler vb.)
                if description:
                    # İlk 3000 karakteri al (çok uzun olabilir)
                    description = description[:3000]
                    # Çok kısa satırları birleştir
                    lines = description.split('\n')
                    clean_lines = []
                    for line in lines:
                        line = line.strip()
                        # Linkleri, hashtag'leri ve özel karakterleri temizle
                        if line and not line.startswith('http') and not line.startswith('#') and len(line) > 10:
                            # Email ve linkleri temizle
                            line = re.sub(r'http\S+|www\.\S+', '', line)
                            line = re.sub(r'\S+@\S+', '', line)
                            if line and len(line.strip()) > 10:
                                clean_lines.append(line.strip())
                    description = ' '.join(clean_lines)
                
                # Başlık ve açıklamayı birleştir
                combined_text = f"{title}"
                if description and len(description) > 50:
                    combined_text += f"\n\n{description}"
                
                if len(combined_text) > 200:
                    print(f"📄 Video başlığı ve açıklaması kullanılıyor... ({len(combined_text)} karakter)")
                    print("💡 Not: Bu video için transkript bulunamadı, sadece başlık ve açıklama analiz edilecek.")
                    return combined_text
                elif len(combined_text) > 20:
                    print(f"⚠️  Sadece video başlığı kullanılıyor... ({len(combined_text)} karakter)")
                    print("💡 Not: Bu video için transkript bulunamadı. Analiz çok sınırlı olacak.")
                    return combined_text
                else:
                    print("❌ Video'da transkript veya yeterli açıklama bulunamadı.")
                    print("💡 Bu video için analiz yapılamıyor.")
                    print("💡 Lütfen transkripti olan başka bir video deneyin.")
                    return ""
                
        except Exception as e:
            print(f"❌ Transkript alınırken hata: {e}")
            raise
    
    def _download_subtitle(self, url: str, lang: str, auto: bool = False) -> str:
        """Alt yazı dosyasını indirir ve metne dönüştürür"""
        try:
            ydl_opts = {
                'writesubtitles': not auto,
                'writeautomaticsub': auto,
                'subtitleslangs': [lang],
                'skip_download': True,
                'quiet': True,
                'no_warnings': False,
                'ignoreerrors': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # VTT dosyasını indir
                if auto:
                    subtitle_url = info.get('automatic_captions', {}).get(lang, [{}])[0].get('url')
                else:
                    subtitle_url = info.get('subtitles', {}).get(lang, [{}])[0].get('url')
                
                if subtitle_url:
                    import requests
                    try:
                        response = requests.get(subtitle_url, timeout=10)
                        response.raise_for_status()
                        subtitle_text = response.text
                        
                        # JSON formatını kontrol et (YouTube'un yeni formatı)
                        if subtitle_text.strip().startswith('{') or 'wireMagic' in subtitle_text or '"events"' in subtitle_text:
                            try:
                                subtitle_data = json.loads(subtitle_text)
                                # JSON formatından metni çıkar
                                clean_text = []
                                if 'events' in subtitle_data:
                                    for event in subtitle_data['events']:
                                        if 'segs' in event:
                                            for seg in event['segs']:
                                                if 'utf8' in seg:
                                                    text = seg['utf8'].strip()
                                                    # Özel karakterleri temizle
                                                    text = text.replace('>>', '').replace('<<', '')
                                                    if text and text != '\n' and len(text) > 0:
                                                        clean_text.append(text)
                                
                                result = ' '.join(clean_text)
                                if result and len(result) > 20:
                                    return result
                            except (json.JSONDecodeError, KeyError) as e:
                                print(f"⚠️  JSON parse hatası: {e}")
                                pass  # JSON değilse VTT olarak işle
                        
                        # VTT formatını temizle
                        lines = subtitle_text.split('\n')
                        clean_text = []
                        for line in lines:
                            line = line.strip()
                            # VTT zaman damgalarını ve HTML etiketlerini kaldır
                            if line and not line.startswith('<') and not re.match(r'^\d+$', line) and not '-->' in line and not line.startswith('WEBVTT') and not line.startswith('NOTE'):
                                # HTML etiketlerini temizle
                                line = re.sub(r'<[^>]+>', '', line)
                                # Özel karakterleri temizle
                                line = line.replace('>>', '').replace('<<', '')
                                if line and len(line) > 1:
                                    clean_text.append(line)
                        
                        result = ' '.join(clean_text)
                        if result and len(result) > 20:
                            return result
                    except requests.RequestException as e:
                        print(f"⚠️  Alt yazı indirme hatası: {e}")
                        return ""
        except Exception as e:
            print(f"⚠️  Alt yazı indirilirken hata: {e}")
        
        return ""
    
    def analyze_sentiment_textblob(self, text: str) -> Dict[str, any]:
        """
        TextBlob ile duygu analizi yapar
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            Duygu analizi sonuçları
        """
        print("😊 Duygu analizi yapılıyor...")
        
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 (negatif) ile 1 (pozitif) arası
        subjectivity = blob.sentiment.subjectivity  # 0 (objektif) ile 1 (subjektif) arası
        
        # Ruh halini belirle
        if polarity > 0.3:
            ruh_hali = "Mutlu 😊"
            duygu = "Pozitif"
        elif polarity > 0.1:
            ruh_hali = "İyi 👍"
            duygu = "Hafif Pozitif"
        elif polarity > -0.1:
            ruh_hali = "Nötr 😐"
            duygu = "Nötr"
        elif polarity > -0.3:
            ruh_hali = "Üzgün 😔"
            duygu = "Hafif Negatif"
        else:
            ruh_hali = "Çok Üzgün/Kızgın 😢"
            duygu = "Negatif"
        
        return {
            'ruh_hali': ruh_hali,
            'duygu': duygu,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'yuzde': round((polarity + 1) * 50, 1)  # 0-100 arası yüzde
        }
    
    def analyze_sentiment_ai(self, text: str) -> Dict[str, any]:
        """
        OpenAI ile gelişmiş duygu analizi yapar
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            Duygu analizi sonuçları
        """
        if not self.client:
            return None
        
        print("🤖 AI ile detaylı duygu analizi yapılıyor...")
        
        try:
            # Metni kısalt (token limiti için)
            text_short = text[:3000] if len(text) > 3000 else text
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir duygu analizi uzmanısın. Verilen metni analiz edip ruh halini, duyguyu ve tonunu belirliyorsun."},
                    {"role": "user", "content": f"""Aşağıdaki metni analiz et ve şunları belirle:
1. Ruh hali (Mutlu, Üzgün, Kızgın, Nötr, Korkulu, Şaşkın, vb.)
2. Genel duygu (Pozitif, Negatif, Nötr)
3. Duygu yoğunluğu (1-10 arası)
4. Kısa açıklama

Metin:
{text_short}

Cevabı şu formatta ver:
Ruh Hali: [ruh hali]
Duygu: [pozitif/negatif/nötr]
Yoğunluk: [1-10]
Açıklama: [kısa açıklama]"""}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            
            # Sonuçları parse et
            result = {
                'ruh_hali': "Bilinmiyor",
                'duygu': "Bilinmiyor",
                'yoğunluk': 5,
                'aciklama': result_text
            }
            
            for line in result_text.split('\n'):
                if 'Ruh Hali:' in line:
                    result['ruh_hali'] = line.split('Ruh Hali:')[1].strip()
                elif 'Duygu:' in line:
                    result['duygu'] = line.split('Duygu:')[1].strip()
                elif 'Yoğunluk:' in line:
                    try:
                        result['yoğunluk'] = int(re.search(r'\d+', line).group())
                    except:
                        pass
                elif 'Açıklama:' in line:
                    result['aciklama'] = line.split('Açıklama:')[1].strip()
            
            return result
            
        except Exception as e:
            print(f"⚠️  AI analizi yapılırken hata: {e}")
            return None
    
    def analyze_video(self, url: str, use_ai: bool = False) -> Dict[str, any]:
        """
        Video URL'sinden duygu analizi yapar
        
        Args:
            url: YouTube video URL'si
            use_ai: OpenAI kullanarak detaylı analiz yap (varsayılan: False)
            
        Returns:
            Analiz sonuçları
        """
        # Transkripti al
        transcript = self.get_video_transcript(url)
        
        if not transcript or len(transcript) < 20:
            error_msg = 'Yeterli transkript bulunamadı'
            if transcript:
                error_msg += f'. Alınan metin çok kısa ({len(transcript)} karakter).'
            else:
                error_msg += '. Video\'da transkript veya yeterli açıklama yok.'
            return {
                'error': error_msg,
                'transcript': transcript if transcript else ''
            }
        
        # Duygu analizi yap
        sentiment = self.analyze_sentiment_textblob(transcript)
        
        # AI analizi (opsiyonel)
        ai_sentiment = None
        if use_ai and self.client:
            ai_sentiment = self.analyze_sentiment_ai(transcript)
        
        return {
            'transcript': transcript,
            'sentiment': sentiment,
            'ai_sentiment': ai_sentiment,
            'transcript_length': len(transcript)
        }


def main():
    print("=" * 60)
    print("🎥 YOUTUBE VİDEO DUYGU ANALİZİ")
    print("=" * 60)
    
    # URL al
    try:
        url = input("\n📺 YouTube video URL'sini girin: ").strip()
        if not url:
            print("❌ URL girilmedi!")
            input("Enter'a basın...")
            return
        
        # URL formatını kontrol et
        if 'youtube.com' not in url and 'youtu.be' not in url:
            print("⚠️  Geçerli bir YouTube URL'si girin!")
            input("Enter'a basın...")
            return
    except (EOFError, KeyboardInterrupt):
        print("\n\n⚠️  Giriş iptal edildi.")
        return
    
    # Analiz yap
    analyzer = VideoDuyguAnalizi()
    
    use_ai = input("\n🤖 AI ile detaylı analiz yapmak istiyor musunuz? (e/h): ").strip().lower() == 'e'
    
    try:
        results = analyzer.analyze_video(url, use_ai=use_ai)
        
        if 'error' in results:
            print(f"\n❌ {results['error']}")
            if results.get('transcript'):
                print(f"Alınan transkript: {results['transcript'][:200]}...")
            input("\n⏸️  Enter'a basın...")
            return
        
        # Sonuçları göster
        print("\n" + "=" * 60)
        print("📊 ANALİZ SONUÇLARI")
        print("=" * 60)
        
        sentiment = results['sentiment']
        print(f"\n😊 Ruh Hali: {sentiment['ruh_hali']}")
        print(f"📈 Duygu: {sentiment['duygu']}")
        print(f"📊 Pozitiflik Oranı: %{sentiment['yuzde']}")
        print(f"📝 Subjektivite: {sentiment['subjectivity']:.2f}")
        
        if results['ai_sentiment']:
            ai = results['ai_sentiment']
            print(f"\n🤖 AI Analizi:")
            print(f"   Ruh Hali: {ai['ruh_hali']}")
            print(f"   Duygu: {ai['duygu']}")
            print(f"   Yoğunluk: {ai['yoğunluk']}/10")
            print(f"   Açıklama: {ai['aciklama']}")
        
        print(f"\n📄 Transkript Uzunluğu: {results['transcript_length']} karakter")
        
        # Transkripti otomatik göster
        print("\n" + "=" * 60)
        print("📝 TRANSKRİPT")
        print("=" * 60)
        transcript = results['transcript']
        if len(transcript) > 2000:
            # Uzun transkriptleri böl
            print(transcript[:2000])
            print("\n... (devam ediyor) ...\n")
            print(transcript[2000:4000] if len(transcript) > 4000 else transcript[2000:])
            if len(transcript) > 4000:
                print(f"\n... (toplam {len(transcript)} karakter, {len(transcript) - 4000} karakter daha var) ...")
        else:
            print(transcript)
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        print("\n🔍 Detaylı hata bilgisi:")
        traceback.print_exc()
        input("\n⏸️  Hata detaylarını görmek için yukarıdaki bilgileri kontrol edin. Enter'a basın...")


if __name__ == "__main__":
    while True:
        try:
            main()
            
            # Kullanıcıya seçenek sun
            print("\n" + "=" * 60)
            print("Ne yapmak istersiniz?")
            print("=" * 60)
            choice = input("\n1️⃣  Yeni video analiz et\n2️⃣  Çıkış\n\nSeçiminiz (1/2): ").strip()
            
            if choice == '2' or choice.lower() == 'çıkış' or choice.lower() == 'cikis':
                print("\n👋 Program sonlandırılıyor. İyi günler!")
                break
            elif choice == '1' or choice.lower() == 'yeni':
                print("\n" + "=" * 60)
                print("YENİ VİDEO ANALİZİ")
                print("=" * 60)
                continue
            else:
                print("\n⚠️  Geçersiz seçim. Program sonlandırılıyor.")
                break
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Program kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            print(f"\n❌ Kritik hata: {e}")
            import traceback
            traceback.print_exc()
            choice = input("\n⏸️  Devam etmek istiyor musunuz? (e/h): ").strip().lower()
            if choice != 'e':
                break

