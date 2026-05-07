@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ===========================================
echo   MARINA SAMOS - UPDATE
echo ===========================================
echo.

cd /d "%~dp0"

set "PYTHON_DIR=%~dp0python_portable"
set "REPO_ZIP_URL=https://github.com/bzaiser/Marina-Administration-and-Booking/archive/refs/heads/main.zip"

if not exist "%PYTHON_DIR%\python.exe" (
    echo [FEHLER] Installation nicht gefunden.
    echo Bitte zuerst setup-marina.bat ausfuehren.
    pause
    exit /b 1
)

:: Download neue Version
echo [1/3] Lade aktuelle Version von GitHub herunter...
powershell -NoProfile -Command "Invoke-WebRequest -Uri '%REPO_ZIP_URL%' -OutFile '%~dp0update_temp.zip'"
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Download fehlgeschlagen. Bitte Internetverbindung pruefen.
    pause
    exit /b 1
)

echo [+] Entpacke Update...
powershell -NoProfile -Command "Expand-Archive -Path '%~dp0update_temp.zip' -DestinationPath '%~dp0update_temp' -Force"

:: Dateien kopieren - Datenbank, Medien und Python bleiben erhalten
echo [+] Aktualisiere Anwendungsdateien...
for /d %%D in ("%~dp0update_temp\*") do (
    powershell -NoProfile -Command ^
        "Copy-Item -Path '%%D\*' -Destination '%~dp0' -Recurse -Force" ^
        " -Exclude @('db.sqlite3','python_portable','media')"
)

rd /s /q "%~dp0update_temp"
del "%~dp0update_temp.zip"
echo [OK] Dateien aktualisiert.
echo.

:: Python-Pakete und Datenbank aktualisieren
echo [2/3] Aktualisiere Abhaengigkeiten...
"%PYTHON_DIR%\python.exe" -m pip install -r requirements.txt --quiet

echo [3/3] Fuehre Migrationen und Vendor-Update aus...
"%PYTHON_DIR%\python.exe" manage.py migrate
"%PYTHON_DIR%\python.exe" manage.py update_vendor

echo.
echo ===========================================
echo   UPDATE ABGESCHLOSSEN!
echo ===========================================
pause

endlocal
