@echo off
setlocal

echo ===========================================
echo   MARINA SAMOS - START
echo ===========================================
echo.

cd /d "%~dp0"

if not exist "python_portable\python.exe" (
    echo [FEHLER] Installation nicht gefunden.
    echo Bitte zuerst setup-marina.bat ausfuehren.
    pause
    exit /b 1
)

echo [+] Starte Server auf Port 8003...
start http://127.0.0.1:8003
"python_portable\python.exe" manage.py runserver 8003

endlocal
