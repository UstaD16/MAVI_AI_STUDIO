@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Backup Manifest

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "MANIFEST=%ROOT%mavi_backup_manifest.py"

echo ============================================================
echo MAVI AI STUDIO
echo BACKUP MANIFEST
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%MANIFEST%" (
    echo [FAIL] mavi_backup_manifest.py bulunamadi:
    echo %MANIFEST%
    echo.
    pause
    exit /b 1
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo MANIFEST OLUSTURULUYOR
echo ============================================================
echo.

"%PYTHON%" "%MANIFEST%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo BACKUP MANIFEST: READY
    echo.
    echo Manifest:
    echo %ROOT%logs\mavi_backup_manifest.json
) else (
    echo BACKUP MANIFEST: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%