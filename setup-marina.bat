@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     MARINA SAMOS - SETUP (Windows)           ║
echo ║     Komplett portable Installation            ║
echo ╚══════════════════════════════════════════════╝
echo.

:: Wechsle zum Verzeichnis des Skripts (Projektroot)
cd /d "%~dp0"

:: ──────────────────────────────────────────────────
:: 1. PORTABLES PYTHON HERUNTERLADEN
:: ──────────────────────────────────────────────────
set "PYTHON_DIR=%~dp0python_portable"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"

echo [1/5] Richte lokales, portables Python ein...
if exist "%PYTHON_DIR%\python.exe" (
    echo [OK] Portables Python bereits vorhanden.
) else (
    echo [+] Lade Python 3.11 Embedded herunter...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python-embed.zip'"
    
    echo [+] Entpacke Python...
    powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath '%PYTHON_DIR%' -Force"
    del "python-embed.zip"
    
    :: pip aktivieren im Embedded Python (import site einkommentieren)
    echo [+] Aktiviere Pip-Unterstuetzung...
    powershell -Command "(Get-Content '%PYTHON_DIR%\python311._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\python311._pth'"
    
    echo [+] Installiere Pip...
    powershell -Command "Invoke-WebRequest -Uri '%PIP_URL%' -OutFile 'get-pip.py'"
    "%PYTHON_DIR%\python.exe" get-pip.py
    del "get-pip.py"
    
    echo [OK] Lokales Python erfolgreich eingerichtet.
)
echo.

:: ──────────────────────────────────────────────────
:: 2. ABHÄNGIGKEITEN INSTALLIEREN
:: ──────────────────────────────────────────────────
echo [2/5] Installiere Abhaengigkeiten...
"%PYTHON_DIR%\python.exe" -m pip install --upgrade pip --quiet
"%PYTHON_DIR%\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Installation der Abhaengigkeiten fehlgeschlagen.
    pause
    exit /b 1
)
echo [OK] Abhaengigkeiten installiert.
echo.

:: ──────────────────────────────────────────────────
:: 3. DATENBANK EINRICHTEN
:: ──────────────────────────────────────────────────
echo [3/5] Richte Datenbank ein...
"%PYTHON_DIR%\python.exe" manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Datenbankmigrationen fehlgeschlagen.
    pause
    exit /b 1
)
echo [OK] Datenbank eingerichtet.
echo.

:: ──────────────────────────────────────────────────
:: 4. LOKALE BIBLIOTHEKEN (FLAGS ETC.)
:: ──────────────────────────────────────────────────
echo [4/5] Lade lokale Bibliotheken (Flaggen, Icons etc.)...
"%PYTHON_DIR%\python.exe" manage.py update_vendor
if %ERRORLEVEL% neq 0 (
    echo [WARNUNG] update_vendor fehlgeschlagen - App laeuft trotzdem.
)
echo [OK] Bibliotheken geladen.
echo.

:: ──────────────────────────────────────────────────
:: 5. DESKTOP-VERKNÜPFUNGEN (OPTIONAL)
:: ──────────────────────────────────────────────────
echo ══════════════════════════════════════════════
set /p ICON_CHOICE="Desktop-Verknuepfungen erstellen? (J/N): "
if /i "!ICON_CHOICE!"=="J" (
    echo [+] Erstelle Desktop-Verknuepfungen...
    powershell -NoProfile -Command ^
        "$desktop = [Environment]::GetFolderPath('Desktop');" ^
        "$dir = '%~dp0'.TrimEnd('\');" ^
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
        "Write-Host '[OK] Verknuepfungen auf dem Desktop erstellt.'"
)
echo.

:: ──────────────────────────────────────────────────
:: ABSCHLUSS
:: ──────────────────────────────────────────────────
echo ╔══════════════════════════════════════════════╗
echo ║   SETUP ABGESCHLOSSEN!                       ║
echo ║                                              ║
echo ║   Starten:   start-marina.bat                ║
echo ║   Updaten:   update-marina.bat               ║
echo ╚══════════════════════════════════════════════╝
echo.
set /p START_CHOICE="App jetzt direkt starten? (J/N): "
if /i "!START_CHOICE!"=="J" (
    echo [+] Starte Marina Administration...
    start http://127.0.0.1:8003
    "%PYTHON_DIR%\python.exe" manage.py runserver 8003
) else (
    echo Tschuess! Starte die App jederzeit mit start-marina.bat
    pause
)

endlocal
