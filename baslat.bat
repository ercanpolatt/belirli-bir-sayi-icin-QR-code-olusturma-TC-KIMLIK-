@echo off
title Barkod & QR Kod Studio
echo Uygulama baslatiliyor, lutfen bekleyin...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Uygulama baslatilamadi. Python ve kutuphanelerin yuklu oldugundan emin olun:
    echo pip install -r requirements.txt
    pause
)
