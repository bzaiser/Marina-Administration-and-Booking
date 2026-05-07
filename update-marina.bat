@echo off
setlocal

echo ==========================================
echo   MARINA SAMOS - UPDATE (Windows)
echo ==========================================
echo.

:: Wechsle zum Verzeichnis des Skripts
cd /d "%~dp0"

:: Git pruefen
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Git nicht gefunden. Bitte Git installieren: https://git-scm.com
    pause
    exit /b 1
)

:: Git Pull
echo [+] Hole Updates von GitHub...
git pull
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Git Pull fehlgeschlagen. Bitte Internetverbindung pruefen.
    pause
    exit /b 1
)

:: Venv und Python-Updates
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [+] Installiere Requirements...
    pip install -r requirements.txt
    echo [+] Fuehre Migrationen aus...
    python manage.py migrate
    echo [+] Aktualisiere lokale Bibliotheken (Flaggen etc.)...
    python manage.py update_vendor
) else (
    echo [WARNUNG] venv nicht gefunden.
)

echo.
echo ==========================================
echo   UPDATE ABGESCHLOSSEN!
echo ==========================================
pause

endlocal
