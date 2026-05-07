@echo off
setlocal

set "WORKDIR=%~dp0"
set "PYTHON_DIR=%WORKDIR%python_portable"

echo.
echo ==========================================
echo   MARINA SAMOS - START
echo ==========================================
echo.

if not exist "%PYTHON_DIR%\python.exe" (
    echo [FEHLER] Installation nicht gefunden.
    echo Bitte zuerst setup-marina.bat ausfuehren.
    pause
    exit /b 1
)

echo [+] Starte Server auf Port 8003...
start http://127.0.0.1:8003
"%PYTHON_DIR%\python.exe" "%WORKDIR%manage.py" runserver 8003

endlocal
