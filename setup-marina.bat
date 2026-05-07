@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     MARINA SAMOS - SETUP (Windows)           ║
echo ║     Erstinstallation / Einrichtung            ║
echo ╚══════════════════════════════════════════════╝
echo.

:: Wechsle zum Verzeichnis des Skripts (Projektroot)
cd /d "%~dp0"

:: ──────────────────────────────────────────────────
:: 1. PYTHON PRÜFEN
:: ──────────────────────────────────────────────────
echo [1/5] Pruefe Python...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo [FEHLER] Python wurde nicht gefunden!
    echo.
    echo Bitte Python 3.10 oder neuer installieren:
    echo https://www.python.org/downloads/
    echo.
    echo WICHTIG: Bei der Installation "Add Python to PATH" aktivieren!
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('python --version 2^>^&1') do set PY_VERSION=%%V
echo [OK] %PY_VERSION% gefunden.
echo.

:: ──────────────────────────────────────────────────
:: 2. VENV ERSTELLEN
:: ──────────────────────────────────────────────────
echo [2/5] Erstelle virtuelle Python-Umgebung (venv)...
if exist "venv\Scripts\activate.bat" (
    echo [OK] venv bereits vorhanden - wird wiederverwendet.
) else (
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [FEHLER] venv konnte nicht erstellt werden.
        pause
        exit /b 1
    )
    echo [OK] venv erstellt.
)
echo.

:: ──────────────────────────────────────────────────
:: 3. ABHÄNGIGKEITEN INSTALLIEREN
:: ──────────────────────────────────────────────────
echo [3/5] Installiere Abhaengigkeiten...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Installation der Abhaengigkeiten fehlgeschlagen.
    pause
    exit /b 1
)
echo [OK] Abhaengigkeiten installiert.
echo.

:: ──────────────────────────────────────────────────
:: 4. DATENBANK EINRICHTEN
:: ──────────────────────────────────────────────────
echo [4/5] Richte Datenbank ein...
python manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo [FEHLER] Datenbankmigrationen fehlgeschlagen.
    pause
    exit /b 1
)
echo [OK] Datenbank eingerichtet.
echo.

:: ──────────────────────────────────────────────────
:: 5. LOKALE BIBLIOTHEKEN (FLAGS ETC.)
:: ──────────────────────────────────────────────────
echo [5/5] Lade lokale Bibliotheken (Flaggen, Icons etc.)...
python manage.py update_vendor
if %ERRORLEVEL% neq 0 (
    echo [WARNUNG] update_vendor fehlgeschlagen - App laeuft trotzdem.
)
echo [OK] Bibliotheken geladen.
echo.

:: ──────────────────────────────────────────────────
:: DESKTOP-VERKNÜPFUNGEN (OPTIONAL)
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
    python manage.py runserver 8003
) else (
    echo Tschuess! Starte die App jederzeit mit start-marina.bat
    pause
)

endlocal
