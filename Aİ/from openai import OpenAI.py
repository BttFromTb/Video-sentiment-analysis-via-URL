from openai import OpenAI

# -----------------------------
#  API ANAHTARINI YAZ
# -----------------------------
client = OpenAI(api_key="BURAYA_API_KEYİNİ_YAZ")

# -----------------------------
# 1) Video → Metin (Transcribe)
# -----------------------------
print("Videoyu metne çeviriyorum...")

transcription = client.audio.transcriptions.create(
    file=open("video.mp4", "rb"),   # video dosyasını aç
    model="gpt-4o-transcribe",      # yeni transcribe modeli
    language="tr"                   # Türkçe videolar için
)

metin = transcription.text

print("\n--- VİDEODAN ÇIKAN METİN ---")
print(metin)


# -----------------------------
# 2) Duygu Analizi (Emotion Detection)
# -----------------------------
print("\nDuygu analizi yapılıyor...")

analysis = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Sen profesyonel bir duygu analizi uzmanısın."},
        {"role": "user", "content": f"Bu metindeki kişinin ruh halini, duygusunu ve konuşma tonunu analiz et: {metin}"}
    ]
)

print("\n--- DUYGU ANALİZİ ---")
print(analysis.choices[0].message["content"])
