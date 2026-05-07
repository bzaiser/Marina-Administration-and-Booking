@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     MARINA SAMOS - SETUP                     ║
echo ║     Alles wird automatisch eingerichtet      ║
echo ╚══════════════════════════════════════════════╝
echo.
echo Benoetigt wird nur eine Internetverbindung.
echo.

set "INSTALL_DIR=%~dp0Marina-Administration"
set "PYTHON_DIR=%INSTALL_DIR%\python_portable"
set "REPO_ZIP_URL=https://github.com/bzaiser/Marina-Administration-and-Booking/archive/refs/heads/main.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"

:: ──────────────────────────────────────────────────
:: 1. ANWENDUNG HERUNTERLADEN
:: ──────────────────────────────────────────────────
echo [1/5] Lade Marina von GitHub herunter...
powershell -NoProfile -Command "Invoke-WebRequest -Uri '%REPO_ZIP_URL%' -OutFile '%~dp0marina_app.zip'"
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Download fehlgeschlagen. Bitte Internetverbindung pruefen.
    pause
    exit /b 1
)

echo [+] Entpacke Anwendung...
if exist "%INSTALL_DIR%" rd /s /q "%INSTALL_DIR%"
powershell -NoProfile -Command "Expand-Archive -Path '%~dp0marina_app.zip' -DestinationPath '%~dp0marina_temp' -Force"
for /d %%D in ("%~dp0marina_temp\*") do move "%%D" "%INSTALL_DIR%" >nul
rd /s /q "%~dp0marina_temp"
del "%~dp0marina_app.zip"
echo [OK] Anwendung heruntergeladen.
echo.

:: ──────────────────────────────────────────────────
:: 2. PORTABLES PYTHON EINRICHTEN
:: ──────────────────────────────────────────────────
echo [2/5] Lade portables Python herunter (einmalig)...
if exist "%PYTHON_DIR%\python.exe" (
    echo [OK] Python bereits vorhanden.
) else (
    powershell -NoProfile -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%~dp0python_embed.zip'"
    powershell -NoProfile -Command "Expand-Archive -Path '%~dp0python_embed.zip' -DestinationPath '%PYTHON_DIR%' -Force"
    del "%~dp0python_embed.zip"

    powershell -NoProfile -Command ^
        "$f = Get-ChildItem '%PYTHON_DIR%' -Filter '*._pth' | Select-Object -First 1;" ^
        "(Get-Content $f.FullName) -replace '#import site','import site' | Set-Content $f.FullName"

    powershell -NoProfile -Command "Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%INSTALL_DIR%\get-pip.py'"
    "%PYTHON_DIR%\python.exe" "%INSTALL_DIR%\get-pip.py" --quiet
    del "%INSTALL_DIR%\get-pip.py"
    echo [OK] Portables Python eingerichtet.
)
echo.

:: ──────────────────────────────────────────────────
:: 3. KONFIGURATION (.env)
:: ──────────────────────────────────────────────────
echo [3/5] Konfiguration der Datenbank...
echo.
echo Wo soll die Datenbank gespeichert werden?
echo.
echo   [1] Lokal im Programmordner (Standard, nur 1 Benutzer)
echo   [2] OneDrive / geteilter Ordner (mehrere Benutzer)
echo.
set /p DB_CHOICE="Auswahl (1 oder 2): "

set "DB_PATH_LINE="

if "!DB_CHOICE!"=="2" (
    echo.
    echo Beispiel: C:\Users\Bernd\OneDrive\Marina\db.sqlite3
    echo.
    set /p ONEDRIVE_PATH="Vollstaendiger Pfad zur Datenbankdatei: "
    set "DB_PATH_LINE=DB_PATH=!ONEDRIVE_PATH!"

    :: OneDrive-Ordner erstellen falls nicht vorhanden
    for %%F in ("!ONEDRIVE_PATH!") do set "ONEDRIVE_FOLDER=%%~dpF"
    if not exist "!ONEDRIVE_FOLDER!" (
        mkdir "!ONEDRIVE_FOLDER!"
        echo [OK] Ordner erstellt: !ONEDRIVE_FOLDER!
    )
    echo [OK] Datenbank wird in OneDrive gespeichert.
) else (
    echo [OK] Datenbank wird lokal gespeichert.
)

:: .env Datei schreiben
echo # Marina Samos - Konfiguration (automatisch erstellt) > "%INSTALL_DIR%\.env"
echo DB_ENGINE=django.db.backends.sqlite3 >> "%INSTALL_DIR%\.env"
if not "!DB_PATH_LINE!"=="" (
    echo !DB_PATH_LINE! >> "%INSTALL_DIR%\.env"
)
echo DEBUG=True >> "%INSTALL_DIR%\.env"
echo ALLOWED_HOSTS=127.0.0.1,localhost >> "%INSTALL_DIR%\.env"
echo [OK] Konfigurationsdatei (.env) erstellt.
echo.

:: ──────────────────────────────────────────────────
:: 4. ABHAENGIGKEITEN + DATENBANK
:: ──────────────────────────────────────────────────
echo [4/5] Installiere Abhaengigkeiten...
"%PYTHON_DIR%\python.exe" -m pip install -r "%INSTALL_DIR%\requirements.txt" --quiet
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Installation fehlgeschlagen.
    pause
    exit /b 1
)
echo [+] Richte Datenbank ein...
"%PYTHON_DIR%\python.exe" "%INSTALL_DIR%\manage.py" migrate
echo [+] Lade lokale Bibliotheken (Flaggen etc.)...
"%PYTHON_DIR%\python.exe" "%INSTALL_DIR%\manage.py" update_vendor
echo [OK] Fertig.
echo.

:: ──────────────────────────────────────────────────
:: 5. DESKTOP-VERKNUEPFUNGEN
:: ──────────────────────────────────────────────────
echo [5/5] Desktop-Verknuepfungen...
set /p ICON_CHOICE="Desktop-Icons erstellen? (J/N): "
if /i "!ICON_CHOICE!"=="J" (
    powershell -NoProfile -Command ^
        "$desktop = [Environment]::GetFolderPath('Desktop');" ^
        "$dir = '%INSTALL_DIR%';" ^
        "$ws = New-Object -ComObject WScript.Shell;" ^
        "$s1 = $ws.CreateShortcut((Join-Path $desktop 'Marina Starten.lnk'));" ^
        "$s1.TargetPath = Join-Path $dir 'start-marina.bat';" ^
        "$s1.WorkingDirectory = $dir;" ^
        "$s1.IconLocation = 'shell32.dll, 167';" ^
        "$s1.Save();" ^
        "$s2 = $ws.CreateShortcut((Join-Path $desktop 'Marina Update.lnk'));" ^
        "$s2.TargetPath = Join-Path $dir 'update-marina.bat';" ^
        "$s2.WorkingDirectory = $dir;" ^
        "$s2.IconLocation = 'shell32.dll, 71';" ^
        "$s2.Save();" ^
        "Write-Host '[OK] Icons auf dem Desktop erstellt.'"
)

:: ──────────────────────────────────────────────────
:: ABSCHLUSS
:: ──────────────────────────────────────────────────
echo.
echo ╔══════════════════════════════════════════════╗
echo ║   SETUP ABGESCHLOSSEN!                       ║
echo ║                                              ║
echo ║   Starten:   Marina-Administration\          ║
echo ║              start-marina.bat               ║
echo ║   Updaten:   Marina-Administration\          ║
echo ║              update-marina.bat              ║
echo ║   Konfig:    Marina-Administration\.env      ║
echo ╚══════════════════════════════════════════════╝
echo.
set /p START_CHOICE="App jetzt direkt starten? (J/N): "
if /i "!START_CHOICE!"=="J" (
    start http://127.0.0.1:8003
    "%PYTHON_DIR%\python.exe" "%INSTALL_DIR%\manage.py" runserver 8003
) else (
    pause
)

endlocal
