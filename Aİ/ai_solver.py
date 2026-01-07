"""
AI ile soru çözme modülü
"""
import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AISolver:
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API anahtarı (opsiyonel, .env'den de alınabilir)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API anahtarı bulunamadı. .env dosyasına OPENAI_API_KEY ekleyin veya parametre olarak verin.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.book_content = None
    
    def set_book_content(self, content: str):
        """Kitap içeriğini ayarlar"""
        self.book_content = content
    
    def solve_question(self, question: str) -> str:
        """
        Soruyu kitap içeriğine göre cevaplar
        
        Args:
            question: Çözülecek soru
            
        Returns:
            Sorunun cevabı
        """
        if not self.book_content:
            raise ValueError("Kitap içeriği ayarlanmamış. set_book_content() metodunu kullanın.")
        
        prompt = f"""Aşağıdaki kitap içeriğini oku ve verilen soruyu kitaba göre cevapla.
Sadece kitapta geçen bilgilere göre cevap ver. Eğer kitapta bilgi yoksa "Kitapta bu bilgi bulunmamaktadır" yaz.

KİTAP İÇERİĞİ:
{self.book_content[:8000]}  # İlk 8000 karakteri kullan (token limiti için)

SORU:
{question}

CEVAP (Kısa ve net):"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir kitap yarışması soru çözme asistanısın. Kitap içeriğine göre soruları cevaplıyorsun."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            raise Exception(f"AI ile soru çözülürken hata oluştu: {str(e)}")

