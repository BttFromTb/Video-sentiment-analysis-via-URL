@echo off
chcp 65001 >nul
echo ========================================
echo YOUTUBE VIDEO DUYGU ANALIZI
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo.
    pause
    exit /b 1
)

echo [OK] Python bulundu
echo.

REM Paketleri kontrol et ve yükle
echo Gerekli paketler kontrol ediliyor...
python -m pip install -r requirements.txt --upgrade
if errorlevel 1 (
    echo [HATA] Paketler yüklenirken hata oluştu!
    echo.
    echo TextBlob için ek veri indiriliyor...
    python -c "import nltk; nltk.download('punkt'); nltk.download('brown')" 2>nul
    pause
    exit /b 1
)

echo [OK] Tüm paketler hazır
echo.
echo Program başlatılıyor...
echo.

python video_duygu_analizi.py

if errorlevel 1 (
    echo.
    echo [HATA] Program çalışırken bir hata oluştu!
    echo.
)

echo.
echo Program sonlandı.
pause

