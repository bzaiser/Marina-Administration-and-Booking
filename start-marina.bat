@echo off
setlocal

echo ===========================================
echo   MARINA SAMOS - START (Windows)
echo ===========================================
echo.

:: Wechsle zum Verzeichnis des Skripts (egal von wo aus gestartet)
cd /d "%~dp0"

:: Pruefen ob venv vorhanden
if not exist "venv\Scripts\activate.bat" (
    echo [FEHLER] venv nicht gefunden. Bitte zuerst Setup ausfuehren.
    echo         python -m venv venv
    echo         venv\Scripts\activate
    echo         pip install -r requirements.txt
    echo         python manage.py migrate
    echo         python manage.py update_vendor
    pause
    exit /b 1
)

:: Venv aktivieren
call venv\Scripts\activate.bat

:: Browser oeffnen und Server starten
echo [+] Starte Server auf Port 8003...
start http://127.0.0.1:8003
python manage.py runserver 8003

endlocal
