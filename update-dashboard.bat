@echo off
setlocal

echo ==========================================
echo   MARINA SAMOS - Update Assistent
echo ==========================================
echo.

:: Check for Git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Git wurde nicht gefunden. Update nicht moeglich.
    pause
    exit /b 1
)

:: Pull latest changes
echo [+] Suche nach Updates auf GitHub...
git pull
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Git Pull fehlgeschlagen. Bitte Internetverbindung pruefen.
    pause
    exit /b 1
)

:: Update System
echo [+] Aktualisiere Datenbank und Bibliotheken...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py update_vendor
) else (
    echo [WARNUNG] Virtuelle Umgebung (venv) nicht gefunden. Ueberspringe Python-Updates.
)

echo.
echo ==========================================
echo   UPDATE ERFOLGREICH!
echo ==========================================
pause
