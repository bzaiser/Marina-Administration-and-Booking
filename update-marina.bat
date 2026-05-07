@echo off
setlocal

set "WORKDIR=%~dp0"
set "PYTHON_DIR=%WORKDIR%python_portable"
set "REPO_ZIP_URL=https://github.com/bzaiser/Marina-Administration-and-Booking/archive/refs/heads/main.zip"

echo.
echo ==========================================
echo   MARINA SAMOS - UPDATE
echo ==========================================
echo.

if not exist "%PYTHON_DIR%\python.exe" (
    echo [FEHLER] Installation nicht gefunden.
    echo Bitte zuerst setup-marina.bat ausfuehren.
    pause
    exit /b 1
)

:: Neue Version herunterladen
echo [1/3] Lade aktuelle Version von GitHub herunter...
powershell -NoProfile -Command "Invoke-WebRequest -Uri '%REPO_ZIP_URL%' -OutFile '%WORKDIR%update_temp.zip'"
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Download fehlgeschlagen. Bitte Internetverbindung pruefen.
    pause
    exit /b 1
)

echo [+] Entpacke Update...
powershell -NoProfile -Command "Expand-Archive -Path '%WORKDIR%update_temp.zip' -DestinationPath '%WORKDIR%update_temp' -Force"

:: Dateien kopieren - Datenbank, Medien und Python bleiben erhalten
echo [+] Aktualisiere Anwendungsdateien...
for /d %%D in ("%WORKDIR%update_temp\*") do (
    powershell -NoProfile -Command "Get-ChildItem '%%D' | Where-Object { $_.Name -notin @('db.sqlite3','python_portable','media','.env') } | Copy-Item -Destination '%WORKDIR%' -Recurse -Force"
)

rd /s /q "%WORKDIR%update_temp"
del "%WORKDIR%update_temp.zip"
echo [OK] Dateien aktualisiert.
echo.

:: Pakete und Datenbank aktualisieren
echo [2/3] Aktualisiere Abhaengigkeiten...
"%PYTHON_DIR%\python.exe" -m pip install -r "%WORKDIR%requirements.txt" --quiet

echo [3/3] Fuehre Migrationen aus...
"%PYTHON_DIR%\python.exe" "%WORKDIR%manage.py" migrate
"%PYTHON_DIR%\python.exe" "%WORKDIR%manage.py" update_vendor

echo.
echo ==========================================
echo   UPDATE ABGESCHLOSSEN!
echo ==========================================
pause

endlocal
