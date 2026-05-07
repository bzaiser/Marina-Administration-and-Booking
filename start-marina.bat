@echo off
setlocal

echo ===========================================
echo   MARINA SAMOS - START (Windows Portable)
echo ===========================================
echo.

:: Wechsle zum Verzeichnis des Skripts
cd /d "%~dp0"

:: Pruefen ob portables Python vorhanden
if not exist "python_portable\python.exe" (
    echo [FEHLER] Portables Python nicht gefunden. 
    echo Bitte zuerst setup-marina.bat ausfuehren.
    pause
    exit /b 1
)

:: Browser oeffnen und Server starten
echo [+] Starte Server auf Port 8003...
start http://127.0.0.1:8003
"python_portable\python.exe" manage.py runserver 8003

endlocal
