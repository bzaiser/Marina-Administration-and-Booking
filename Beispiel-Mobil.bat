@echo off
setlocal enabledelayedexpansion

echo ===========================================
echo   MARINA SAMOS - MOBILE EDITION (PORTABLE)
echo ===========================================
echo.

set "DOWNLOAD_URL=https://github.com/bzaiser/Marina-Administration-and-Booking/archive/refs/heads/main.zip"
set "TARGET_DIR=Marina-Administration"

:: 1. PRUEFEN OB ORDNER EXISTIERT
if exist "%TARGET_DIR%" (
    echo [+] Ordner gefunden.
    set /p UPDATE_CHOICE="Nach Updates suchen? (J/N): "
    if /i "!UPDATE_CHOICE!"=="J" goto DOWNLOAD
    goto START_APP
)

:DOWNLOAD
echo [+] Lade aktuelle Version von GitHub...
powershell -command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile 'app.zip'"
echo [+] Entpacke Dateien...
powershell -command "Expand-Archive -Path 'app.zip' -DestinationPath 'temp_extract' -Force"

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
for /d %%D in (temp_extract\*) do (
    echo [+] Aktualisiere Dateien...
    xcopy /E /I /Y /Q "%%D\*" "%TARGET_DIR%\"
)

rd /S /Q temp_extract
del "app.zip"

:SETUP
echo [+] Erstelle isolierte Python-Umgebung (Venv)...
cd /d "%TARGET_DIR%"
if not exist "venv" (
    python -m venv venv
)

echo [+] Installiere notwendige Module...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py update_vendor

REM --- DESKTOP ICONS INSTALLATION ---
echo.
set /p ICON_CHOICE="Desktop-Icons (Start & Wartung) erstellen? (J/N): "
if /i "!ICON_CHOICE!" NEQ "J" goto START_APP

echo [+] Erstelle Verknuepfungen auf dem Desktop...
powershell -NoProfile -Command "$d=[Environment]::GetFolderPath('Desktop');$ws=New-Object -ComObject WScript.Shell;$curr=(Get-Location).Path;$root=(Get-Item $curr).Parent.FullName;$s1=$ws.CreateShortcut((Join-Path $d 'Marina Start.lnk'));$s1.TargetPath=(Join-Path $curr 'venv\Scripts\python.exe');$s1.Arguments='manage.py runserver 8003';$s1.WorkingDirectory=$curr;$s1.IconLocation='shell32.dll, 167';$s1.Save();$s2=$ws.CreateShortcut((Join-Path $d 'Marina Wartung.lnk'));$s2.TargetPath=(Join-Path $root 'Beispiel-Mobil.bat');$s2.WorkingDirectory=$root;$s2.IconLocation='shell32.dll, 71';$s2.Save();if($?){Write-Host '[+] Icons erfolgreich erstellt!' -ForegroundColor Green}else{Write-Host '[FEHLER] Icons fehlgeschlagen' -ForegroundColor Red}"

:START_APP
echo [+] Starte Marina Administration...
cd /d "%TARGET_DIR%"
call venv\Scripts\activate.bat
start http://127.0.0.1:8003
python manage.py runserver 8003
exit /b 0
