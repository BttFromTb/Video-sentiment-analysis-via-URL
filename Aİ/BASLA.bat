@echo off
chcp 65001 >nul
echo ========================================
echo KİTAP YARIŞMASI OTOMASYONU
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo.
    echo Lütfen önce Python'u yükleyin:
    echo https://www.python.org/downloads/
    echo.
    echo Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın!
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM Paketleri kontrol et ve yükle
echo Gerekli paketler kontrol ediliyor...
python -m pip show selenium >nul 2>&1
if errorlevel 1 (
    echo Paketler yükleniyor... (Bu biraz zaman alabilir)
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [HATA] Paketler yüklenirken hata oluştu!
        pause
        exit /b 1
    )
)

echo [OK] Tüm paketler hazır
echo.

REM .env dosyası kontrolü
if not exist .env (
    echo [UYARI] .env dosyası bulunamadı!
    echo.
    echo Lütfen .env dosyası oluşturun ve içine şunu yazın:
    echo OPENAI_API_KEY=your_api_key_here
    echo.
    echo API anahtarınızı https://platform.openai.com/api-keys adresinden alabilirsiniz.
    echo.
    pause
)

echo Program başlatılıyor...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [HATA] Program çalışırken bir hata oluştu!
    pause
)

