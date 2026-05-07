@echo off
setlocal

echo ==========================================
echo   MARINA SAMOS - UPDATE (Windows Portable)
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

:: Updates mit portablem Python ausfuehren
if exist "python_portable\python.exe" (
    echo [+] Installiere Requirements...
    "python_portable\python.exe" -m pip install -r requirements.txt
    
    echo [+] Fuehre Migrationen aus...
    "python_portable\python.exe" manage.py migrate
    
    echo [+] Aktualisiere lokale Bibliotheken (Flaggen etc.)...
    "python_portable\python.exe" manage.py update_vendor
) else (
    echo [FEHLER] Portables Python nicht gefunden. Bitte setup-marina.bat ausfuehren.
)

echo.
echo ==========================================
echo   UPDATE ABGESCHLOSSEN!
echo ==========================================
pause

endlocal
