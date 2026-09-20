@echo off
setlocal EnableExtensions

title MAVI AI STUDIO - Project Snapshot

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\python.exe"
set "SNAPSHOT=%ROOT%mavi_project_snapshot.py"

echo ============================================================
echo MAVI AI STUDIO
echo PROJECT SNAPSHOT
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo [FAIL] Ana Python bulunamadi:
    echo %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%SNAPSHOT%" (
    echo [FAIL] mavi_project_snapshot.py bulunamadi:
    echo %SNAPSHOT%
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%backup" (
    mkdir "%ROOT%backup"
)

cd /d "%ROOT%"

echo Python:
"%PYTHON%" --version
echo.

echo ============================================================
echo SNAPSHOT OLUSTURULUYOR
echo ============================================================
echo.

"%PYTHON%" "%SNAPSHOT%"

set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================

if "%EXIT_CODE%"=="0" (
    echo PROJECT SNAPSHOT: SUCCESS
    echo.
    echo Yedek klasoru:
    echo %ROOT%backup
) else (
    echo PROJECT SNAPSHOT: FAILED
)

echo ============================================================
echo.

pause
exit /b %EXIT_CODE%